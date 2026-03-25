from io import BytesIO
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_pdf_report(title, headers, data):
    """
    Generates a generic PDF report from headers and a list of lists (data).
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.alignment = 1 # Center
    
    # Title
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 12))
    
    # Subtitle with date
    date_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    elements.append(Paragraph(f"Gerado em: {date_str}", styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Table Data
    table_data = [headers] + data
    
    # Create Table
    t = Table(table_data)
    
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
