import io
from flask import send_file
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from app.services.list_service import ListService

def generate_pdf_report(title, headers, row_data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Spacer(1, 20))
    
    # Table
    data = [headers] + row_data
    t = Table(data)
    
    # Style
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
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
    for t in tarefas:
        dt_cad = t.data_cadastro.strftime("%d/%m/%Y") if t.data_cadastro else ""
        dt_exec = t.data_executado.strftime("%d/%m/%Y") if t.data_executado else ""
        data.append([
            str(t.id),
            t.descricao[:40],
            t.status.denominacao if t.status else "",
            t.grupo.denominacao if t.grupo else "",
            dt_cad,
            dt_exec
        ])
    return generate_pdf_report("Relatório de Tarefas", headers, data)

def build_lists_pdf(lista_obj):
    headers = ["Item", "Grupo", "Status", "Valor (R$)"]
    data = []
    total = 0
    for it in lista_obj.itens:
        if it.valor:
            total += it.valor
        data.append([
            it.item[:40],
            it.grupo.denominacao if it.grupo else "",
            "Comprado" if it.status else "Pendente",
            f"{it.valor:.2f}" if it.valor else ""
        ])
    
    title = f"Lista: {lista_obj.denominacao} | Total est: R$ {total:.2f}"
    return generate_pdf_report(title, headers, data)


class PDFService:
    @staticmethod
    def generate_list_pdf(lista_id):
        # Retrieve list info using existing service
        lista, grupos = ListService.get_list_detail(lista_id)
        if not lista:
            return None

        # Build PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4, 
            rightMargin=30, leftMargin=30, 
            topMargin=30, bottomMargin=30,
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
                    
        resumo_table = Table(
            [[f"Comprado: R$ {comprado:.2f}", f"Pendente: R$ {total - comprado:.2f}", f"Total Estimado: R$ {total:.2f}"]],
            colWidths=['33%', '33%', '34%']
        )
        resumo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#e8f5e9')), # green light
            ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#e3f2fd')), # blue light
            ('BACKGROUND', (2, 0), (2, 0), colors.HexColor('#f5f5f5')), # gray
            ('TEXTCOLOR', (0, 0), (0, 0), colors.HexColor('#2e7d32')),
            ('TEXTCOLOR', (1, 0), (1, 0), colors.HexColor('#1565c0')),
            ('TEXTCOLOR', (2, 0), (2, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.white),
        ]))
        
        if total > 0:
            elements.append(resumo_table)
            elements.append(Spacer(1, 20))

        # Table Headers
        data = [["Status", "Item", "Categoria", "Valor (R$)"]]
        
        # Populate Table Rows
        for it in lista.itens:
            check = "[ X ]" if it.status else "[   ]"
            nome = it.item[:50] + '...' if len(it.item) > 50 else it.item
            categoria = it.grupo.denominacao.upper() if it.grupo else 'OUTROS'
            valor = f"{it.valor:.2f}" if it.valor else "--"
            data.append([check, nome, categoria, valor])

        # Formatting table
        item_table = Table(data, colWidths=[50, 275, 120, 90])
        table_style = TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#313338')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'), # Status Centered
            ('ALIGN', (1, 0), (2, -1), 'LEFT'),   # Name/Category Left
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),  # Prices Right
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            # Lines
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.lightgrey),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ])
        
        # Alternate row colors and strikethrough logic (fallback to gray text)
        for i, row in enumerate(data[1:], start=1):
            if i % 2 == 0:
                table_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f9f9f9'))
            
            # If item is checked, make it gray
            if lista.itens[i-1].status:
                table_style.add('TEXTCOLOR', (0, i), (-1, i), colors.HexColor('#9ca3af'))
            else:
                table_style.add('TEXTCOLOR', (0, i), (-1, i), colors.HexColor('#1f2937'))
                
            table_style.add('FONTNAME', (0, i), (-1, i), 'Helvetica')
            table_style.add('FONTSIZE', (0, i), (-1, i), 9)
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
