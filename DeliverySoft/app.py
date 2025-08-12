
import streamlit as st
import pandas as pd
import plotly.express as px

def analyze_delivery_data(uploaded_file):
    """
    Legge un file Excel, calcola i KPI per i canali di delivery e restituisce un DataFrame.
    """
    try:
        df = pd.read_excel(uploaded_file, sheet_name='CALCOLO', engine='openpyxl')
    except Exception as e:
        st.error(f"Errore nella lettura del file Excel: {e}")
        return None

    # L'estrazione dei dati si basa sulla struttura specifica del file fornito.
    # Se la struttura cambia, questi indici andranno aggiornati.
    channels = ['APP INTERNA', 'DELIVEROO', 'JUST EAT', 'UBER EATS', 'GLOVO']
    data = []

    # Mappatura delle righe nel file Excel per ogni KPI
    kpi_rows = {
        'Scontrino medio netto IVA': 15,
        'Food & Beverage Cost': 21,
        'Commissioni in %': 24,
        'Commissioni in €': 25,
        'Costo consegna': 29,
        'Margine lordo per scontrino': 33,
        'Numero ordini mensili': 38,
        'Ricavo totale': 41,
        'Margine lordo totale': 44
    }

    # Mappatura delle colonne nel file Excel per ogni canale
    channel_cols = {
        'APP INTERNA': 'D',
        'DELIVEROO': 'E',
        'JUST EAT': 'F',
        'UBER EATS': 'G',
        'GLOVO': 'H'
    }
    
    # Convertiamo le lettere delle colonne in indici numerici (base 0)
    # 'A' -> 0, 'B' -> 1, etc.
    channel_col_indices = {name: ord(col.upper()) - ord('A') for name, col in channel_cols.items()}


    for channel in channels:
        col_idx = channel_col_indices.get(channel)
        if col_idx is None:
            continue
            
        channel_data = {'Canale': channel}
        for kpi, row_idx in kpi_rows.items():
            # L'indice della riga in pandas è row_idx - 1
            value = df.iloc[row_idx - 1, col_idx]
            channel_data[kpi] = value
        data.append(channel_data)

    if not data:
        st.warning("Nessun dato estratto. Controlla la struttura del file Excel e i nomi dei canali.")
        return None

    results_df = pd.DataFrame(data)
    return results_df

def highlight_best_margin(s):
    """
    Evidenzia la riga con il margine lordo totale più alto.
    """
    is_max = s['Margine lordo totale'] == s['Margine lordo totale'].max()
    return ['background-color: lightgreen' if v else '' for v in is_max]

def main():
    """
    Funzione principale per eseguire l'app Streamlit.
    """
    st.set_page_config(page_title="Analisi Performance Delivery", layout="wide")

    # --- CSS Personalizzato e HTML ---
    st.markdown("""
        <style>
            .main-title {
                font-size: 2.5rem;
                font-weight: bold;
                color: #2E8B57; /* Verde Marino Scuro */
                text-align: center;
                padding-bottom: 20px;
            }
            .content-box {
                border: 1px solid #ddd;
                border-radius: 10px;
                padding: 25px;
                margin-bottom: 30px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                background-color: #f9f9f9;
            }
            .st-emotion-cache-1kyxreq { /* Stile per il contenitore del file uploader */
                 border: 2px dashed #2E8B57;
                 border-radius: 10px;
            }
        </style>
    """, unsafe_allow_html=True)

    # --- Interfaccia Streamlit ---

    st.markdown('<p class="main-title">📊 Analisi Performance Canali Delivery</p>', unsafe_allow_html=True)

    st.write("""
    Questa applicazione analizza i dati di performance dei canali di delivery di un ristorante 
    caricati da un file Excel. 
    """)

    # Caricamento del file
    uploaded_file = st.file_uploader(
        "Carica il tuo file Excel 'Calcolo_Margine_e_performance_per_canali_delivery.xlsx'",
        type=['xlsx']
    )

    if uploaded_file is not None:
        results_df = analyze_delivery_data(uploaded_file)

        if results_df is not None and not results_df.empty:
            
            # --- Blocco HTML per la Tabella ---
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            st.header("📈 Tabella Riassuntiva dei KPI per Canale")

            # Formattazione numerica per una migliore leggibilità
            formatted_df = results_df.copy()
            
            # Colonne da formattare come valuta
            currency_cols = ['Scontrino medio netto IVA', 'Food & Beverage Cost', 'Commissioni in €', 'Costo consegna', 
                             'Margine lordo per scontrino', 'Ricavo totale', 'Margine lordo totale']
            for col in currency_cols:
                formatted_df[col] = formatted_df[col].apply(lambda x: f'€ {x:,.2f}' if pd.notnull(x) else 'N/D')
            
            # Colonna da formattare come percentuale
            formatted_df['Commissioni in %'] = formatted_df['Commissioni in %'].apply(lambda x: f'{x:.2%}' if pd.notnull(x) else 'N/D')
            
            # Applica lo stile per evidenziare il canale migliore
            styled_df = formatted_df.style.apply(highlight_best_margin, axis=1, subset=pd.IndexSlice[:, ['Canale', 'Margine lordo totale']])
            
            st.dataframe(styled_df, use_container_width=True)
            
            best_channel = results_df.loc[results_df['Margine lordo totale'].idxmax()]
            st.success(f"🎉 Il canale con il **miglior margine lordo totale** è **{best_channel['Canale']}** con un margine di € {best_channel['Margine lordo totale']:.2f}.")
            st.markdown('</div>', unsafe_allow_html=True)


            # --- Blocco HTML per il Grafico ---
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            st.header("📊 Grafici Comparativi")

            # Grafico a barre: Ricavo Totale vs Margine Lordo Totale
            fig = px.bar(
                results_df,
                x='Canale',
                y=['Ricavo totale', 'Margine lordo totale'],
                title='Ricavo Totale vs. Margine Lordo Totale per Canale',
                labels={'value': 'Importo in €', 'variable': 'Metrica'},
                barmode='group', # per avere barre raggruppate
                color_discrete_map={
                    'Ricavo totale': '#1f77b4', # Blu
                    'Margine lordo totale': '#2ca02c'  # Verde
                }
            )
            fig.update_layout(
                xaxis_title="Canale di Delivery",
                yaxis_title="Importo in Euro (€)",
                legend_title="Metriche",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
    else:
        st.info("In attesa del caricamento di un file Excel.")
        st.write("Assicurati che il file abbia un foglio chiamato 'CALCOLO' e che la struttura dei dati sia quella prevista.")

    st.sidebar.header("Istruzioni")
    st.sidebar.write("""
    1.  **Prepara il file Excel**: Assicurati che il tuo file Excel si chiami `Calcolo_Margine_e_performance_per_canali_delivery.xlsx` (o simile) e contenga un foglio di lavoro denominato `CALCOLO`.
    2.  **Struttura del file**: I dati per i canali (APP INTERNA, DELIVEROO, etc.) devono trovarsi nelle colonne da D a H, e i KPI nelle righe specificate nel codice.
    3.  **Carica il file**: Usa il pulsante 'Browse files' per caricare il tuo file.
    4.  **Analizza i risultati**: La tabella e il grafico verranno generati automaticamente. La riga del canale con il miglior margine sarà evidenziata in verde.
    """)

    st.sidebar.header("Informazioni")
    st.sidebar.info("Questa applicazione è stata creata da un assistente AI per l'analisi dei dati di delivery.")

if __name__ == '__main__':
    main() 
