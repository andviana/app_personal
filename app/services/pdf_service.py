import io
from flask import send_file
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from app.services.list_service import ListService

def generate_pdf_report(title, headers, row_data, colWidths=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=18)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles with size 10 and leading 12 for cells to auto-wrap text
    cell_style = ParagraphStyle(
        'CellText',
        parent=styles['Normal'],
        fontSize=10,
        leading=12,
        textColor=colors.black
    )
    header_style = ParagraphStyle(
        'HeaderCellText',
        parent=styles['Normal'],
        fontSize=10,
        leading=12,
        textColor=colors.whitesmoke,
        fontName='Helvetica-Bold',
        alignment=1 # Center
    )
    
    # Title
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Spacer(1, 20))
    
    # Wrap headers and rows in Paragraphs to prevent overflowing cell limits
    wrapped_headers = [Paragraph(str(h), header_style) for h in headers]
    wrapped_rows = []
    for row in row_data:
        wrapped_row = []
        for cell in row:
            wrapped_row.append(Paragraph(str(cell), cell_style))
        wrapped_rows.append(wrapped_row)
        
    data = [wrapped_headers] + wrapped_rows
    t = Table(data, colWidths=colWidths)
    
    # Style
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(t)
    doc.build(elements)
    
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

def build_tasks_pdf(tarefas):
    headers = ["ID", "Descrição", "Status", "Grupo", "Cadastro", "Execução"]
    data = []
    
    status_priority = {'INICIADO': 0, 'PENDENTE': 1, 'FINALIZADO': 2}
    sorted_tarefas = sorted(
        tarefas,
        key=lambda t: (
            t.grupo.denominacao.upper() if t.grupo else '',
            status_priority.get(t.status.denominacao.upper() if t.status else 'PENDENTE', 9)
        )
    )
    
    for t in sorted_tarefas:
        dt_cad = t.data_cadastro.strftime("%d/%m/%Y") if t.data_cadastro else ""
        dt_exec = t.data_executado.strftime("%d/%m/%Y") if t.data_executado else ""
        data.append([
            str(t.id),
            t.descricao,
            t.status.denominacao if t.status else "",
            t.grupo.denominacao if t.grupo else "",
            dt_cad,
            dt_exec
        ])
    colWidths = [40, 340, 90, 120, 89, 90]
    return generate_pdf_report("Relatório de Tarefas", headers, data, colWidths=colWidths)

def build_lists_pdf(lista_obj):
    headers = ["Item", "Grupo", "Status", "Valor (R$)"]
    data = []
    total = 0
    for it in lista_obj.itens:
        if it.valor:
            total += it.valor
        data.append([
            it.item,
            it.grupo.denominacao if it.grupo else "",
            "Comprado" if it.status else "Pendente",
            f"{it.valor:.2f}" if it.valor else ""
        ])
    
    title = f"Lista: {lista_obj.denominacao} | Total est: R$ {total:.2f}"
    colWidths = [360, 160, 120, 129]
    return generate_pdf_report(title, headers, data, colWidths=colWidths)


class PDFService:
    @staticmethod
    def generate_list_pdf(lista_id):
        # Retrieve list info using existing service
        lista, grupos = ListService.get_list_detail(lista_id)
        if not lista:
            return None

        # Build PDF in memory with landscape layout and 36pt margins
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=landscape(A4), 
            rightMargin=36, leftMargin=36, 
            topMargin=36, bottomMargin=36,
            title=f"Lista - {lista.denominacao}"
        )

        elements = []
        styles = getSampleStyleSheet()

        # Styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2b2d31'),
            spaceAfter=10
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.gray,
            spaceAfter=20
        )

        # Header Title
        elements.append(Paragraph(f"📝 {lista.denominacao.upper()}", title_style))
        tipo_nome = lista.tipo.denominacao if lista.tipo else 'Genérica'
        elements.append(Paragraph(f"TIPO: {tipo_nome.upper()} | ITENS: {len(lista.itens)}", subtitle_style))
        elements.append(Spacer(1, 10))

        # Financial Summary
        total = 0.0
        comprado = 0.0
        for it in lista.itens:
            if it.valor:
                total += it.valor
                if it.status:
                    comprado += it.valor

        # Summary Styles
        summary_base = ParagraphStyle(
            'SummaryText',
            parent=styles['Normal'],
            fontSize=10,
            leading=12,
            alignment=1 # Center
        )
        summary_green = ParagraphStyle('SumGreen', parent=summary_base, textColor=colors.HexColor('#2e7d32'), fontName='Helvetica-Bold')
        summary_blue = ParagraphStyle('SumBlue', parent=summary_base, textColor=colors.HexColor('#1565c0'), fontName='Helvetica-Bold')
        summary_dark = ParagraphStyle('SumDark', parent=summary_base, textColor=colors.black, fontName='Helvetica-Bold')

        resumo_table = Table(
            [[
                Paragraph(f"Comprado: R$ {comprado:.2f}", summary_green),
                Paragraph(f"Pendente: R$ {total - comprado:.2f}", summary_blue),
                Paragraph(f"Total Estimado: R$ {total:.2f}", summary_dark)
            ]],
            colWidths=[256, 256, 257] # Sums to 769 (landscape A4 available width)
        )
        resumo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#e8f5e9')), # green light
            ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#e3f2fd')), # blue light
            ('BACKGROUND', (2, 0), (2, 0), colors.HexColor('#f5f5f5')), # gray
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.white),
        ]))
        
        if total > 0:
            elements.append(resumo_table)
            elements.append(Spacer(1, 20))

        # Cell and Header Styles with size 10 and auto-wrap support
        header_center = ParagraphStyle('HC', parent=styles['Normal'], fontSize=10, leading=12, textColor=colors.white, fontName='Helvetica-Bold', alignment=1)
        header_left = ParagraphStyle('HL', parent=styles['Normal'], fontSize=10, leading=12, textColor=colors.white, fontName='Helvetica-Bold', alignment=0)
        header_right = ParagraphStyle('HR', parent=styles['Normal'], fontSize=10, leading=12, textColor=colors.white, fontName='Helvetica-Bold', alignment=2)

        cell_center = ParagraphStyle('CC', parent=styles['Normal'], fontSize=10, leading=12, textColor=colors.HexColor('#1f2937'), alignment=1)
        cell_left = ParagraphStyle('CL', parent=styles['Normal'], fontSize=10, leading=12, textColor=colors.HexColor('#1f2937'), alignment=0)
        cell_right = ParagraphStyle('CR', parent=styles['Normal'], fontSize=10, leading=12, textColor=colors.HexColor('#1f2937'), alignment=2)

        cell_center_checked = ParagraphStyle('CCC', parent=cell_center, textColor=colors.HexColor('#9ca3af'))
        cell_left_checked = ParagraphStyle('CLC', parent=cell_left, textColor=colors.HexColor('#9ca3af'))
        cell_right_checked = ParagraphStyle('CRC', parent=cell_right, textColor=colors.HexColor('#9ca3af'))

        # Table Headers wrapped in Paragraph
        data = [[
            Paragraph("Status", header_center),
            Paragraph("Item", header_left),
            Paragraph("Categoria", header_left),
            Paragraph("Valor (R$)", header_right)
        ]]
        
        # Populate Table Rows
        for it in lista.itens:
            check = "[ X ]" if it.status else "[   ]"
            nome = it.item
            categoria = it.grupo.denominacao.upper() if it.grupo else 'OUTROS'
            valor = f"{it.valor:.2f}" if it.valor else "--"
            
            c_center = cell_center_checked if it.status else cell_center
            c_left = cell_left_checked if it.status else cell_left
            c_right = cell_right_checked if it.status else cell_right

            data.append([
                Paragraph(check, c_center),
                Paragraph(nome, c_left),
                Paragraph(categoria, c_left),
                Paragraph(valor, c_right)
            ])

        # Formatting table
        item_table = Table(data, colWidths=[60, 429, 160, 120]) # Sums to 769 (landscape A4 available width)
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#313338')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.lightgrey),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ])
        
        # Alternate row backgrounds
        for i in range(1, len(data)):
            if i % 2 == 0:
                table_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f9f9f9'))
            table_style.add('BOTTOMPADDING', (0, i), (-1, i), 6)
            table_style.add('TOPPADDING', (0, i), (-1, i), 6)

        item_table.setStyle(table_style)
        elements.append(item_table)

        # Build PDF
        doc.build(elements)

        # Send file response
        buffer.seek(0)
        filename = f"DayLog_Lista_{lista.id}.pdf"
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
