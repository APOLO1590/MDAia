function renderPositionsChart(puestos) {
    const labels = puestos.map(p => p.puesto);
    const values = puestos.map(p => p.percentage);
    
    const data = [{
        values: values,
        labels: labels,
        type: 'pie',
        textinfo: 'label+percent',
        insidetextorientation: 'radial',
        marker: {
            colors: ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        }
    }];
    
    const layout = {
        height: 400,
        margin: {"t": 0, "b": 0, "l": 0, "r": 0}
    };
    
    Plotly.newPlot('positions-chart', data, layout);
}

function renderForecastChart(predictions) {
    const months = predictions.map(p => p.ds);
    const yhat = predictions.map(p => p.yhat);
    const lower = predictions.map(p => p.yhat_lower);
    const upper = predictions.map(p => p.yhat_upper);
    
    const trace1 = {
        x: months,
        y: upper,
        type: 'scatter',
        mode: 'lines',
        line: {width: 0},
        name: 'Límite superior'
    };
    
    const trace2 = {
        x: months,
        y: yhat,
        type: 'scatter',
        mode: 'lines',
        line: {color: '#4285F4'},
        name: 'Predicción'
    };
    
    const trace3 = {
        x: months,
        y: lower,
        type: 'scatter',
        mode: 'lines',
        line: {width: 0},
        fillcolor: 'rgba(66, 133, 244, 0.2)',
        fill: 'tonexty',
        name: 'Límite inferior'
    };
    
    const data = [trace1, trace2, trace3];
    
    const layout = {
        title: 'Pronóstico de Accidentes',
        xaxis: {title: 'Mes'},
        yaxis: {title: 'Número de Accidentes'},
        hovermode: 'closest'
    };
    
    Plotly.newPlot('forecast-chart', data, layout);
}

function renderForecastTable(predictions) {
    const tableBody = document.getElementById('forecast-table');
    tableBody.innerHTML = '';
    
    predictions.forEach(pred => {
        const row = document.createElement('tr');
        
        const monthCell = document.createElement('td');
        monthCell.textContent = pred.ds;
        row.appendChild(monthCell);
        
        const yhatCell = document.createElement('td');
        yhatCell.textContent = pred.yhat.toFixed(1);
        row.appendChild(yhatCell);
        
        const lowerCell = document.createElement('td');
        lowerCell.textContent = pred.yhat_lower.toFixed(1);
        row.appendChild(lowerCell);
        
        const upperCell = document.createElement('td');
        upperCell.textContent = pred.yhat_upper.toFixed(1);
        row.appendChild(upperCell);
        
        tableBody.appendChild(row);
    });
}