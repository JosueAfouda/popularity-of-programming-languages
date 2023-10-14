# Importation des packages
from shiny import App, render, ui, reactive
import pandas as pd
import numpy as np
from pathlib import Path
from plotnine import ggplot, aes, geom_line, theme, element_text, labs

# Importation et préparation des données
def load_data():
    return pd.read_csv(Path(__file__).parent / 'PopularityofProgrammingLanguagesfrom2004to2023.csv')

def data_preparation():
    raw_data = load_data()
    raw_data['Date'] = pd.to_datetime(raw_data['Date'], format='%B %Y')
    long_data = raw_data.melt(
        id_vars='Date',
        value_name='popularity',
        var_name='langage'
    ).reset_index(drop=True)
    return long_data

clean_data = data_preparation()
date_start = np.min(clean_data['Date'])
date_end = np.max(clean_data['Date'])
noms = clean_data['langage'].unique()
noms_dict = {l:l for l in noms}

# Interface Utilisateur
app_ui = ui.page_fluid(
    ui.panel_title("Popularité des langages de Programmation"),
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_selectize(
                id='langage',
                label="Choisis un ou plusieurs langages :",
                choices=noms_dict,
                selected="Python",
                multiple=True
            ),
            ui.input_date_range(
                id='date_range',
                label="Choisis une période :",
                start=date_start,
                end=date_end
            ),
        ),
        ui.panel_main(
            ui.output_plot("PlotTimeserie")
        )
    ),
)

# Serveur (backend)
def server(input, output, session):
    @reactive.Calc
    def filtered_data():
        date_selected_start = pd.to_datetime(input.date_range()[0])
        date_selected_end = pd.to_datetime(input.date_range()[1])

        df = clean_data.loc[(clean_data['langage'].isin(list(input.langage()))) &
                            (clean_data['Date'] >= date_selected_start) &
                            (clean_data['Date'] <= date_selected_end)].reset_index(drop=True)
        
        return df

    
    @output
    @render.plot
    def PlotTimeserie():
        g = ggplot(filtered_data()) + \
        aes(x = 'Date', y = 'popularity', color = 'langage') + \
        geom_line() + \
        labs(x = 'Date', y = 'Popularity [%]', title = 'Popularity over Time') + \
        theme(axis_text=element_text(rotation=90, hjust=1))
        return g


app = App(app_ui, server)
