import os
import json
from datetime import datetime
from typing import Dict, List, Any
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import uuid


class PDFGenerator:

    def __init__(self, output_dir: str = "pdfs"):
        self.output_dir = output_dir
        self.ensure_output_dir()

    def ensure_output_dir(self):
        """ Crear directorio de salida si no existe """
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_filename(self, title: str = None) -> str:
        """ Generar un nombre de archivo único para el PDF """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]  # Generar un ID único corto

        if title:
            # Limpiar titulo para nombre de archivo
            clean_title = "".join(
                c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            clean_title = clean_title.replace(
                " ", "_")[:20]  # Limitar a 20 caracteres
            return f"{clean_title}_{timestamp}_{unique_id}.pdf"

        return f"document_{timestamp}_{unique_id}.pdf"

    def create_reporte_pdf(self, reporte_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Crear PDF específico para el formato de reporte

        Args:
            reporte_data: Diccionario con los datos del reporte

        Returns:
            Dict con información del archivo generado
        """
        try:
            # Generar nombre de archivo basado en fecha
            fecha_str = reporte_data.get('fecha', '').replace('-', '')
            filename = f"reporte_{fecha_str}_{datetime.now().strftime('%H%M%S')}.pdf"
            file_path = os.path.join(self.output_dir, filename)

            # Crear documento PDF
            doc = SimpleDocTemplate(
                file_path,
                pagesize=A4,
                rightMargin=50,
                leftMargin=50,
                topMargin=50,
                bottomMargin=50
            )

            story = []
            styles = getSampleStyleSheet()

            # Estilos personalizados
            title_style = ParagraphStyle(
                'ReporteTitle',
                parent=styles['Title'],
                fontSize=20,
                alignment=TA_CENTER,
                textColor=colors.darkblue,
                spaceAfter=30
            )

            subtitle_style = ParagraphStyle(
                'ReporteSubtitle',
                parent=styles['Heading2'],
                fontSize=14,
                alignment=TA_CENTER,
                textColor=colors.grey,
                spaceAfter=20
            )

            section_style = ParagraphStyle(
                'SectionTitle',
                parent=styles['Heading3'],
                fontSize=12,
                textColor=colors.darkblue,
                spaceAfter=10,
                spaceBefore=15
            )

            # TÍTULO PRINCIPAL
            story.append(Paragraph("REPORTE DE SEGUIMIENTO", title_style))

            # INFORMACIÓN GENERAL
            fecha_hora = f"{reporte_data.get('fecha', 'N/A')} - {reporte_data.get('hora', 'N/A')}"
            story.append(
                Paragraph(f"Fecha y Hora: {fecha_hora}", subtitle_style))

            # DIMENSIONES
            if reporte_data.get('dimensiones'):
                story.append(Paragraph("DIMENSIONES EVALUADAS", section_style))
                dimensiones_text = ", ".join(reporte_data['dimensiones'])
                story.append(
                    Paragraph(f"<b>Dimensiones:</b> {dimensiones_text}", styles['Normal']))
                story.append(Spacer(1, 15))

            # OBJETIVO
            if reporte_data.get('objetivo'):
                story.append(Paragraph("OBJETIVO", section_style))
                story.append(
                    Paragraph(reporte_data['objetivo'], styles['Normal']))
                story.append(Spacer(1, 15))

            # ASPECTOS RELEVANTES
            if reporte_data.get('aspectos'):
                story.append(Paragraph("ASPECTOS RELEVANTES", section_style))
                story.append(
                    Paragraph(reporte_data['aspectos'], styles['Normal']))
                story.append(Spacer(1, 15))

            # AVANCES
            if reporte_data.get('avances'):
                story.append(Paragraph("AVANCES LOGRADOS", section_style))
                story.append(
                    Paragraph(reporte_data['avances'], styles['Normal']))
                story.append(Spacer(1, 15))

            # RETOS
            if reporte_data.get('retos'):
                story.append(Paragraph("RETOS IDENTIFICADOS", section_style))
                story.append(
                    Paragraph(reporte_data['retos'], styles['Normal']))
                story.append(Spacer(1, 15))

            # OPORTUNIDADES
            if reporte_data.get('oportunidades'):
                story.append(
                    Paragraph("OPORTUNIDADES DE MEJORA", section_style))
                story.append(
                    Paragraph(reporte_data['oportunidades'], styles['Normal']))
                story.append(Spacer(1, 15))


            # COMPROMISOS
            if reporte_data.get('compromisos') and len(reporte_data['compromisos']) > 0:
                story.append(Paragraph("COMPROMISOS ADQUIRIDOS", section_style))

                # Estilo para el contenido de las celdas
                cell_style = ParagraphStyle(
                    'CellStyle',
                    parent=styles['Normal'],  # Asegúrate de tener 'styles' definido
                    fontSize=9,
                    leading=11,
                    wordWrap='LTR',
                    alignment=0  # Alineación izquierda
                )

                # Crear tabla de compromisos
                compromisos_data = [
                    [
                        Paragraph("Descripción", styles['Heading4']),
                        Paragraph("Fecha de Cumplimiento", styles['Heading4']),
                        Paragraph("Responsable", styles['Heading4'])
                    ]
                ]

                for compromiso in reporte_data['compromisos']:
                    # Convertir cada campo a Paragraph para manejo correcto del texto
                    descripcion = Paragraph(compromiso.get('descripcion', ''), cell_style)
                    fecha = Paragraph(compromiso.get('fecha_cumplimiento', ''), cell_style)
                    responsable = Paragraph(compromiso.get('responsable', ''), cell_style)

                    compromisos_data.append([descripcion, fecha, responsable])

                # Crear tabla con anchos ajustados
                compromisos_table = Table(compromisos_data, colWidths=[4*inch, 1.5*inch, 1*inch])

                compromisos_table.setStyle(TableStyle([
                    # Estilo para encabezados
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkcyan),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('TOPPADDING', (0, 0), (-1, 0), 12),
                    # Estilo para contenido
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Alineación vertical superior
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    # Padding para mejor legibilidad
                    ('TOPPADDING', (0, 1), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ]))

                story.append(compromisos_table)
                story.append(Spacer(1, 20))

            # PARTICIPANTES
            if reporte_data.get('participantes') and len(reporte_data['participantes']) > 0:
                story.append(Paragraph("PARTICIPANTES", section_style))

                # Crear tabla de participantes
                participantes_data = [["Nombre", "Rol"]]
                for participante in reporte_data['participantes']:
                    participantes_data.append([
                        participante.get('nombre', ''),
                        participante.get('rol', '')
                    ])

                participantes_table = Table(
                    participantes_data, colWidths=[3*inch, 3*inch])
                participantes_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 9)
                ]))
                story.append(participantes_table)
                story.append(Spacer(1, 20))

            # PIE DE PÁGINA
            story.append(Spacer(1, 30))
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                alignment=TA_CENTER,
                textColor=colors.grey
            )
            story.append(Paragraph(
                f"Documento generado automáticamente el {datetime.now().strftime('%d/%m/%Y a las %H:%M:%S')}",
                footer_style
            ))

            # Construir PDF
            doc.build(story)

            return {
                "success": True,
                "filename": filename,
                "file_path": file_path,
                "message": "Reporte PDF generado exitosamente"
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error generando reporte PDF: {str(e)}",
                "filename": None,
                "file_path": None
            }
