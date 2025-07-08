# app.py (backend con Flask)
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
import pandas as pd
import numpy as np
from datetime import datetime
from prophet import Prophet
import os
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


class AccidentAnalyzer:
    def __init__(self, file_path=None):
        self.file_path = file_path
        self.df_2023 = None
        self.df_2024 = None
        self.combined_df = None
        if file_path:
            self.load_data()

    def load_data(self):
        """Carga y prepara los datos del archivo Excel"""
        try:
            # Leer datos de 2024
            df_2024 = pd.read_excel(self.file_path, sheet_name='ACC. 2024', header=3)
            df_2024 = df_2024.dropna(how='all').reset_index(drop=True)
            df_2024 = df_2024.iloc[:, 2:14]
            df_2024.columns = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
            df_2024['Año'] = 2024
            df_2024['Metrica'] = df_2024.index.map({
                0: 'No. De accidentes',
                1: 'no. De trabajadores',
                2: 'Dias cargdados',
                3: 'Dias de incapacidad',
                4: 'Frecuencia de accidentalidad',
                5: 'Severidad de accidentalidad',
                6: 'operario',
                7: 'mensajero',
                8: 'Vendedor',
                9: 'Gerente',
                10: 'Hombre',
                11: 'mujer'
            })
            
            # Leer datos de 2023
            df_2023 = pd.read_excel(self.file_path, sheet_name='ACC.2023', header=3)
            df_2023 = df_2023.dropna(how='all').reset_index(drop=True)
            df_2023 = df_2023.iloc[:, 2:14]
            df_2023.columns = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
            df_2023['Año'] = 2023
            df_2023['Metrica'] = df_2023.index.map({
                0: 'No. De accidentes',
                1: 'no. De trabajadores',
                2: 'Dias cargdados',
                3: 'Dias de incapacidad',
                4: 'Frecuencia de accidentalidad',
                5: 'Severidad de accidentalidad',
                6: 'operario',
                7: 'mensajero',
                8: 'Vendedor',
                9: 'Gerente',
                10: 'Hombre',
                11: 'mujer'
            })
            
            self.df_2023 = df_2023
            self.df_2024 = df_2024
            
            # Combinar datos
            combined = pd.concat([df_2023, df_2024])
            self.combined_df = combined.melt(id_vars=['Año', 'Metrica'], 
                                        var_name='Mes', 
                                        value_name='Valor')
            
            # Asegurar que la columna 'Valor' sea numérica
            self.combined_df['Valor'] = pd.to_numeric(self.combined_df['Valor'], errors='coerce')
            
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False

    def get_summary_stats(self):
        """Calcula estadísticas resumidas"""
        if self.combined_df is None:
            return None
            
        accidentes = self.combined_df[self.combined_df['Metrica'] == 'No. De accidentes']
        stats = {
            'total_accidentes': int(accidentes['Valor'].sum()),
            'avg_per_month': float(accidentes['Valor'].mean()),
            'max_month': accidentes.groupby('Mes')['Valor'].mean().idxmax(),
            'max_month_value': float(accidentes.groupby('Mes')['Valor'].mean().max()),
            'min_month': accidentes.groupby('Mes')['Valor'].mean().idxmin(),
            'min_month_value': float(accidentes.groupby('Mes')['Valor'].mean().min())
        }
        
        # Por puesto de trabajo
        puestos = ['operario', 'mensajero', 'Vendedor', 'Gerente']
        puesto_data = self.combined_df[self.combined_df['Metrica'].isin(puestos)]
        puesto_sum = puesto_data.groupby('Metrica')['Valor'].sum().sort_values(ascending=False)
        
        stats['puestos'] = []
        for puesto, valor in puesto_sum.items():
            stats['puestos'].append({
                'puesto': puesto,
                'total': int(valor),
                'percentage': float((valor / stats['total_accidentes']) * 100)
            })
        
        return stats

    def predict_accidents(self, periods=12):
        """Realiza predicciones para periodos futuros"""
        if self.combined_df is None:
            return None
            
        # Preparar datos para Prophet
        accidentes = self.combined_df[self.combined_df['Metrica'] == 'No. De accidentes']
        
        # Mapping de nombres de meses en español a números
        month_map = {
            'Enero': 1, 'Febrero': 2, 'Marzo': 3, 'Abril': 4, 
            'Mayo': 5, 'Junio': 6, 'Julio': 7, 'Agosto': 8, 
            'Septiembre': 9, 'Octubre': 10, 'Noviembre': 11, 'Diciembre': 12
        }
        
        # Convertir nombres de meses a fechas usando el mapeo
        accidentes['Fecha'] = accidentes.apply(
            lambda x: datetime(year=int(x['Año']), month=month_map[x['Mes']], day=1), 
            axis=1
        )
        
        accidentes = accidentes.sort_values('Fecha')
        prophet_data = accidentes[['Fecha', 'Valor']].rename(columns={'Fecha': 'ds', 'Valor': 'y'})
        
        # Ya que Prophet está comentado, generamos datos simulados para pruebas
        import numpy as np
        last_date = datetime.now()
        future_dates = [last_date + pd.DateOffset(months=i) for i in range(1, periods+1)]
        
        forecast_df = pd.DataFrame({
            'ds': future_dates,
            'yhat': np.random.uniform(1, 10, periods),
            'yhat_lower': np.random.uniform(0, 5, periods),
            'yhat_upper': np.random.uniform(5, 15, periods)
        })
        
        # Convertir fechas al formato esperado
        forecast_df['ds'] = forecast_df['ds'].dt.strftime('%B %Y')
        
        return forecast_df.to_dict('records')

# Rutas de Flask
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    filename = request.args.get('file')
    if not filename:
        return redirect(url_for('index'))
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    try:
        analyzer = AccidentAnalyzer(filepath)
        if analyzer.load_data():
            stats = analyzer.get_summary_stats()
            predictions = analyzer.predict_accidents()
            
            return render_template('dashboard.html',
                               filename=filename,
                               stats=stats,
                               predictions=predictions)
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/dashboard.html')
def dashboard_html():
    filename = request.args.get('file')
    return redirect(url_for('dashboard', file=filename))

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file and file.filename.endswith('.xlsx'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        analyzer = AccidentAnalyzer(filepath)
        if analyzer.load_data():
            return jsonify({'success': True, 'filename': filename})
        else:
            return jsonify({'error': 'Error processing file'}), 500
    else:
        return jsonify({'error': 'Invalid file type'}), 400

@app.route('/analyze/<filename>')
def analyze_data(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    analyzer = AccidentAnalyzer(filepath)
    analyzer.load_data()
    
    stats = analyzer.get_summary_stats()
    predictions = analyzer.predict_accidents()
    
    return jsonify({
        'stats': stats,
        'predictions': predictions
    })

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run(debug=True)