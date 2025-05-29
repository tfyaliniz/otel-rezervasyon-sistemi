import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from datetime import datetime
import os

# Font dosyasının yolu
FONT_PATH = os.path.join('static', 'fonts', 'DejaVuSans.ttf')

def create_excel_report(bookings, stats):
    """Excel raporu oluşturur"""
    output = BytesIO()
    
    # Rezervasyon verilerini DataFrame'e dönüştür
    booking_data = []
    for booking in bookings:
        booking_data.append({
            'Rezervasyon No': booking.id,
            'Müşteri': booking.user.name,
            'Oda': f"{booking.room.room_number} - {booking.room.room_type}",
            'Giriş Tarihi': booking.check_in.strftime('%d/%m/%Y'),
            'Çıkış Tarihi': booking.check_out.strftime('%d/%m/%Y'),
            'Süre (Gün)': booking.duration,
            'Tutar': f"₺{booking.total_price:.2f}",
            'Durum': booking.status,
            'Değerlendirme': booking.rating if booking.rating else '-'
        })
    
    # İstatistik verilerini DataFrame'e dönüştür
    stats_data = [{
        'Metrik': 'Toplam Rezervasyon',
        'Değer': stats['total_bookings']
    }, {
        'Metrik': 'Toplam Gelir',
        'Değer': f"₺{stats['total_revenue']:.2f}"
    }, {
        'Metrik': 'İptal Oranı',
        'Değer': f"%{stats['cancellation_rate']:.1f}"
    }, {
        'Metrik': 'Ortalama Değerlendirme',
        'Değer': f"{stats['avg_rating']:.1f}/5"
    }]
    
    # Excel yazıcısı oluştur
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Rezervasyonlar sayfası
        df_bookings = pd.DataFrame(booking_data)
        df_bookings.to_excel(writer, sheet_name='Rezervasyonlar', index=False)
        
        # İstatistikler sayfası
        df_stats = pd.DataFrame(stats_data)
        df_stats.to_excel(writer, sheet_name='İstatistikler', index=False)
        
        # Grafik verileri sayfası
        df_monthly = pd.DataFrame({
            'Tarih': stats['monthly_revenue_dates'],
            'Gelir': stats['monthly_revenue_data']
        })
        df_monthly.to_excel(writer, sheet_name='Aylık Gelir', index=False)
        
        df_occupancy = pd.DataFrame({
            'Sezon': ['Kış', 'İlkbahar', 'Yaz', 'Sonbahar'],
            'Doluluk Oranı (%)': stats['seasonal_occupancy_data']
        })
        df_occupancy.to_excel(writer, sheet_name='Sezonluk Doluluk', index=False)
        
        # Excel dosyasını formatla
        workbook = writer.book
        
        # Para birimi formatı
        money_format = workbook.add_format({'num_format': '₺#,##0.00'})
        percent_format = workbook.add_format({'num_format': '0.0%'})
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
        
        # Rezervasyonlar sayfasını formatla
        worksheet = writer.sheets['Rezervasyonlar']
        worksheet.set_column('A:A', 15)  # Rezervasyon No
        worksheet.set_column('B:B', 25)  # Müşteri
        worksheet.set_column('C:C', 25)  # Oda
        worksheet.set_column('D:E', 15)  # Tarihler
        worksheet.set_column('F:F', 12)  # Süre
        worksheet.set_column('G:G', 15)  # Tutar
        worksheet.set_column('H:H', 15)  # Durum
        worksheet.set_column('I:I', 15)  # Değerlendirme
        
        # Başlık formatı
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4CAF50',
            'color': 'white',
            'align': 'center',
            'valign': 'vcenter'
        })
        for col_num, value in enumerate(df_bookings.columns.values):
            worksheet.write(0, col_num, value, header_format)
    
    output.seek(0)
    return output

def create_pdf_report(bookings, stats):
    """PDF raporu oluşturur"""
    output = BytesIO()
    
    # PDF dokümanı oluştur
    doc = SimpleDocTemplate(
        output,
        pagesize=landscape(A4),
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )
    
    # Türkçe font ekle
    pdfmetrics.registerFont(TTFont('DejaVuSans', FONT_PATH))
    
    # Stil tanımlamaları
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Heading1'],
        fontName='DejaVuSans',
        fontSize=16,
        spaceAfter=30
    ))
    styles.add(ParagraphStyle(
        name='CustomBody',
        parent=styles['Normal'],
        fontName='DejaVuSans',
        fontSize=10
    ))
    
    # Rapor içeriği
    elements = []
    
    # Başlık
    title = Paragraph(f"Otel Rezervasyon Raporu - {datetime.now().strftime('%d/%m/%Y')}", styles['CustomTitle'])
    elements.append(title)
    
    # İstatistikler tablosu
    stats_data = [
        ['Metrik', 'Değer'],
        ['Toplam Rezervasyon', str(stats['total_bookings'])],
        ['Toplam Gelir', f"₺{stats['total_revenue']:.2f}"],
        ['İptal Oranı', f"%{stats['cancellation_rate']:.1f}"],
        ['Ortalama Değerlendirme', f"{stats['avg_rating']:.1f}/5"]
    ]
    
    stats_table = Table(stats_data)
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.green),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(stats_table)
    elements.append(Spacer(1, 20))
    
    # Rezervasyonlar tablosu
    booking_data = [['Rezervasyon No', 'Müşteri', 'Oda', 'Giriş', 'Çıkış', 'Süre', 'Tutar', 'Durum']]
    for booking in bookings:
        booking_data.append([
            booking.id,
            booking.user.name,
            f"{booking.room.room_number} - {booking.room.room_type}",
            booking.check_in.strftime('%d/%m/%Y'),
            booking.check_out.strftime('%d/%m/%Y'),
            f"{booking.duration} gün",
            f"₺{booking.total_price:.2f}",
            booking.status
        ])
    
    booking_table = Table(booking_data)
    booking_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.green),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(booking_table)
    
    # PDF oluştur
    doc.build(elements)
    output.seek(0)
    return output 