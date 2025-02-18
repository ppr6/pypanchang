from flask import current_app
from flask_mail import Mail, Message
from bs4 import BeautifulSoup
import re

mail = Mail()

def parse_panchang_data(raw_data):
    """Parse the raw panchang data into structured format"""
    soup = BeautifulSoup(raw_data, 'html.parser')
    text_content = soup.get_text()
    
    # Split the text into lines and clean them
    lines = [line.strip() for line in text_content.split('\n') if line.strip()]
    
    data = {
        'location': lines[0],  # First line is location
        'date': lines[1],      # Second line is date
        'shaka': lines[2],     # Shaka details
        'vikrami_north': lines[3],  # Vikrami North
        'vikrami_gujarat': lines[4],  # Vikrami Gujarat
    }
    
    # Process the remaining lines
    for line in lines[5:]:
        if '🔆' in line:
            data['sunrise_sunset'] = line.replace('🔆', '').strip()
        elif '🌙' in line:
            data['moonrise_moonset'] = line.replace('🌙', '').strip()
        elif 'Tamil:' in line:
            data['tamil'] = line
        elif 'Paksha' in line:
            data['paksha'] = line
        elif 'till' in line:
            # Handle various 'till' cases
            if 'Rahukalam:' in line:
                data['rahukalam'] = line
            elif 'Yamagandam:' in line:
                data['yamagandam'] = line
            elif 'Gulikai:' in line:
                data['gulikai'] = line
            elif 'Abhijit:' in line:
                data['abhijit'] = line
            elif 'Durmuhurtham:' in line:
                data['durmuhurtham'] = line
            elif 'Varjyam:' in line:
                data['varjyam'] = line
            elif 'Amritkalam:' in line:
                data['amritkalam'] = line
            else:
                # Other 'till' cases (Tithi, Nakshatra, etc.)
                key = line.split(' till')[0].lower()
                data[key] = line
        elif 'Sun:' in line:
            data['sun'] = line
        elif 'Moon:' in line:
            data['moon'] = line
        elif 'Sayana Sun:' in line:
            data['sayana_sun'] = line
        elif 'Sun Star:' in line:
            data['sun_star'] = line
        elif 'DikShoolai:' in line:
            data['dikshoolai'] = line
        elif 'Kaal Vaasa:' in line:
            data['kaal_vaasa'] = line
        elif 'Rahu Vaasa:' in line:
            data['rahu_vaasa'] = line
        elif 'Agnivasa:' in line:
            data['agnivasa'] = line
        elif 'Moon abode:' in line:
            if 'moon_abode' not in data:
                data['moon_abode'] = []
            data['moon_abode'].append(line)
        elif 'Shraddha Tithi' in line:
            data['shraddha_tithi'] = line
    
    return data

def create_email_html(city_name, date, panchang_data):
    """Create HTML email content with a beautiful card design"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .panchang-card {{
                max-width: 600px;
                margin: 0 auto;
                font-family: Arial, sans-serif;
                background: #ffffff;
                border-radius: 12px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            .card-header {{
                background: #4a90e2;
                color: white;
                padding: 20px;
                text-align: center;
            }}
            .card-body {{
                padding: 20px;
            }}
            .greeting {{
                text-align: center;
                font-size: 1.2em;
                color: #333;
                margin-bottom: 20px;
                padding: 10px;
            }}
            .info-section {{
                margin: 15px 0;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 8px;
            }}
            .info-title {{
                color: #4a90e2;
                font-weight: bold;
                margin-bottom: 10px;
            }}
            .info-content {{
                color: #333;
                line-height: 1.5;
            }}
            .footer {{
                text-align: center;
                padding: 20px;
                color: #666;
                font-size: 12px;
            }}
            .divider {{
                border-top: 1px solid #eee;
                margin: 10px 0;
            }}
        </style>
    </head>
    <body>
        <div class="greeting">
            Namaste, here is your daily panchang for {city_name}:
        </div>
        <div class="panchang-card">
            <div class="card-header">
                <h2>{panchang_data.get('location', city_name)}</h2>
                <p>{panchang_data.get('date', date)}</p>
            </div>
            <div class="card-body">
    """
    
    # Calendar Systems
    html += f"""
    <div class="info-section">
        <div class="info-title">Calendar Systems</div>
        <div class="info-content">
            {panchang_data.get('shaka', '')}<br>
            {panchang_data.get('vikrami_north', '')}<br>
            {panchang_data.get('vikrami_gujarat', '')}<br>
            {panchang_data.get('tamil', '')}
        </div>
    </div>
    """
    
    # Sun and Moon
    html += f"""
    <div class="info-section">
        <div class="info-title">☀️ Sun and Moon Timings</div>
        <div class="info-content">
            Sunrise/Sunset: {panchang_data.get('sunrise_sunset', '')}<br>
            Moonrise/Moonset: {panchang_data.get('moonrise_moonset', '')}<br>
            {panchang_data.get('sun', '')}<br>
            {panchang_data.get('moon', '')}<br>
            {panchang_data.get('sayana_sun', '')}<br>
            {panchang_data.get('sun_star', '')}
        </div>
    </div>
    """
    
    # Panchang Elements
    html += f"""
    <div class="info-section">
        <div class="info-title">Panchang Elements</div>
        <div class="info-content">
            {panchang_data.get('paksha', '')}<br>
            Tithi: {panchang_data.get('shashti', '')}<br>
            Nakshatra: {panchang_data.get('chitra', '')}<br>
            Yoga: {panchang_data.get('ganda', '')}<br>
            Karana: {panchang_data.get('garaja', '')}<br>
            {panchang_data.get('vanija', '')}
        </div>
    </div>
    """
    
    # Auspicious/Inauspicious Timings
    html += f"""
    <div class="info-section">
        <div class="info-title">⏰ Important Timings</div>
        <div class="info-content">
            {panchang_data.get('rahukalam', '')}<br>
            {panchang_data.get('yamagandam', '')}<br>
            {panchang_data.get('gulikai', '')}<br>
            {panchang_data.get('abhijit', '')}<br>
            {panchang_data.get('durmuhurtham', '')}<br>
            {panchang_data.get('varjyam', '')}<br>
            {panchang_data.get('amritkalam', '')}
        </div>
    </div>
    """
    
    # Directional Information
    html += f"""
    <div class="info-section">
        <div class="info-title">🧭 Directional Information</div>
        <div class="info-content">
            {panchang_data.get('dikshoolai', '')}<br>
            {panchang_data.get('kaal_vaasa', '')}<br>
            {panchang_data.get('rahu_vaasa', '')}<br>
            {panchang_data.get('agnivasa', '')}
        </div>
    </div>
    """
    
    # Moon Abode
    if 'moon_abode' in panchang_data:
        html += f"""
        <div class="info-section">
            <div class="info-title">🌙 Moon Abode</div>
            <div class="info-content">
                {'<br>'.join(panchang_data['moon_abode'])}
            </div>
        </div>
        """
    
    # Shraddha Tithi
    if 'shraddha_tithi' in panchang_data:
        html += f"""
        <div class="info-section">
            <div class="info-title">Shraddha Tithi</div>
            <div class="info-content">
                {panchang_data['shraddha_tithi']}
            </div>
        </div>
        """
    
    # Close the HTML
    html += """
            </div>
            <div class="footer">
                <p>To manage your subscription preferences, please visit our website.</p>
                <p style="font-size: 10px; color: #888;">Panchang data provided by MyPanchang (<a href="https://mypanchang.com/" style="color: #4a90e2; text-decoration: none;">https://mypanchang.com/</a>). All credits for the data go to MyPanchang.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

def send_panchang_email(user_email, city_name, panchang_data):
    """Send panchang email to a user"""
    try:
        parsed_data = parse_panchang_data(panchang_data['raw_data'])
        html_content = create_email_html(
            city_name,
            panchang_data['date'],
            parsed_data
        )
        
        msg = Message(
            subject="PyPanchang: Your Daily Panchang",
            recipients=[user_email],
            html=html_content
        )
        
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Error sending email to {user_email}: {str(e)}")
        return False 