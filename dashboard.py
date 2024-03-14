import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO
import plotly.express as px
import requests




# Cargar los datos

## data para analisis de titulos
## data_platform para analisis de  platform
## data_exclusive para analsis de exclusivas


# load data

url = 'https://raw.githubusercontent.com/ereyesb/ign-dashbd/main/IGN_games_from_best_to_worst.csv'

response = requests.get(url)

# Verificar si la descarga fue exitosa
if response.status_code == 200:
    # Leer el contenido del archivo CSV
    csv_data = response.content.decode('utf-8')
    
    # Convertir el contenido a un DataFrame de Pandas
    data = pd.read_csv(StringIO(csv_data))
    
    # Ahora puedes usar el DataFrame `df` como lo harías normalmente
    print(data.head())
else:
    print("No se pudo descargar el archivo CSV")
  
data_original = data

# Paleta de colores

custom_colors = ['#053061', '#2166ac', '#4393c3', '#92c5de', '#d1e5f0', '#f7f7f7', '#fddbc7', '#f4a582', '#d6604d', '#b2182b']
exclusive_colors = {'Nintendo': 'red', 'Sony Playstation': 'blue', 'Microsoft Xbox': 'green'}

# Data manipulation

data = data.query('release_year != 1970').drop(columns = ['release_month', 'release_day']).dropna()


lista_platform = ['Game Boy Color',
                  'Game Boy',
                  'Wii',
                  'Game Boy Advance',
                  'Nintendo 64',
                  'GameCube',
                  'Wii U',
                  'Nintendo 3DS',
                  'Nintendo DS',
                  'Nintendo DSi',
                  'Super NES',
                  'NES',
                  'PlayStation 3',
                  'PlayStation 4',
                  'PlayStation 2',
                  'PlayStation',
                  'PlayStation Portable',
                  'PlayStation Vita',
                  'Xbox',
                  'Xbox 360',
                  'Xbox One',
                  'PC']

lista_system = ['Nintendo',
                'Nintendo',
                'Nintendo',
                'Nintendo',
                'Nintendo',
                'Nintendo',
                'Nintendo',
                'Nintendo',
                'Nintendo',
                'Nintendo',
                'Nintendo',
                'Nintendo',
                'Sony Playstation',
                'Sony Playstation',
                'Sony Playstation',
                'Sony Playstation',
                'Sony Playstation',
                'Sony Playstation',
                'Microsoft Xbox',
                'Microsoft Xbox',
                'Microsoft Xbox',
                'Microsoft Xbox']

df_system = pd.DataFrame({'platform': lista_platform, 'system': lista_system})

data =  pd.merge(data, df_system, on='platform', how='left').fillna('Other')

data_platform = data.copy()

# Realizar la agrupación por la columna 'Grupo' y aplicar la función de agregación personalizada
resultado = pd.crosstab(index=data['title'], columns=data['system'])

microsoft_exclusives = resultado[(resultado['Microsoft Xbox'] >= 1) & (resultado['Nintendo'] == 0) & (resultado['Other'] == 0) & (resultado['Sony Playstation'] == 0)]
microsoft_exclusives = pd.merge(microsoft_exclusives, data, on='title', how='left').fillna('Other')


sony_exclusives = resultado[(resultado['Microsoft Xbox'] == 0) & (resultado['Nintendo'] == 0) & (resultado['Other'] == 0) & (resultado['Sony Playstation'] >= 1)]
sony_exclusives = pd.merge(sony_exclusives, data, on='title', how='left').fillna('Other')

nintendo_exclusives = resultado[(resultado['Microsoft Xbox'] == 0) & (resultado['Nintendo'] >= 1) & (resultado['Other'] == 0) & (resultado['Sony Playstation'] == 0)]
nintendo_exclusives = pd.merge(nintendo_exclusives, data, on='title', how='left').fillna('Other')


data_exclusivos = pd.concat([microsoft_exclusives, sony_exclusives, nintendo_exclusives], axis=0)

# Eliminar duplicados basados en title
data = data.drop_duplicates(subset=['title']).drop(columns=['platform', 'system'])





# Convertir la columna 'release_year' a tipo datetime
## data['release_year'] = pd.to_datetime(data['release_year'], format='%Y')

# Obtener el rango mínimo y máximo de fechas
min_date = data['release_year'].min()
max_date = data['release_year'].max()


### ---- LINEPLOTS -----------


#  Contar las ocurrencias de cada categoría de 'variable_y' en todo el conjunto de datos
count_genre = data['genre'].value_counts().reset_index().rename(columns={'index': 'genre', 'genre': 'count'})

# Ordenar las ocurrencias de la variable_y de mayor a menor
count_genre_t10 = count_genre.sort_values(by='count', ascending=False).head(10)['genre']

# Contar las ocurrencias de cada categoría de 'genre' para cada año
count_data = data.groupby(['release_year', 'genre']).size().reset_index(name='count')

# Filtrar el DataFrame count_data utilizando las 10 principales categorías
count_data_filtered = count_data[count_data['genre'].isin(count_genre_t10)]

## REPETIR PARA PLATFORM

count_platform = data_platform['platform'].value_counts().reset_index().rename(columns={'index': 'platform', 'platform' : 'count'})
count_platform_t10 = count_platform.sort_values(by='count', ascending=False).head(10)['platform'] # TOP 10

count_data_platform = data_platform.groupby(['release_year', 'platform']).size().reset_index(name='count')
count_data_filtered_pf = count_data_platform[count_data_platform['platform'].isin(count_platform_t10)]


### ---- BOXPLOT -----------

data_t10_genre = data[data['genre'].isin(count_genre_t10)]

# Crear la aplicación Streamlit


def main():
    st.set_page_config(
        page_title = "IGN Dashboard",
        page_icon = ":bar_chart:",
        layout = "wide"
    )
    # Título de la aplicación
    st.title("IGN Game score Dashboard")
    

    # Crear una barra lateral para la navegación
    menu = ["Home", "Titles and Platforms", "Exclusives Analysis"]
    choice = st.sidebar.selectbox("Navigation", menu)

    # Mostrar el contenido según la opción seleccionada
    if choice == "Home":
        show_data()
    elif choice == "Titles and Platforms":
        show_dashboard1()
    elif choice == "Exclusives Analysis":
        show_dashboard_exclusivos()

def show_data():

    tab1, tab2, tab3 = st.tabs(["Data", "Data description", "Data manipulation"])

    with tab1:

        st.title("Resume")
        
        ## st.write("Poner mejor y peores juegos y un buscador")
        st.write("This dashboard application entails the analysis of ratings assigned by the renowned media IGN to all games released up to 2016. You can explore detailed information in the tabs provided on this page.")
        st.write("The analysis has two focuses: firstly, the analysis of titles, genres, and platforms; and secondly, the analysis of exclusive titles and the performance of the Sony, Nintendo, and Xbox brands.")
        st.write("If you want to find the score of a specific title, you can search for it below.")
        with st.expander('Search for your game:'):
            txt_input = st.text_input("Game title:")
            if not txt_input:
                st.write("")
            else:
                   st.dataframe(
                        data_original[data_original["title"].str.contains(txt_input, case=False)],
                        column_config ={
                                        "release_year": st.column_config.NumberColumn(format="%d")
                                        }
                                )

        
        
        st.divider()
        st.subheader("About IGN")
        st.write("IGN is an American video game and entertainment media website operated by IGN Entertainment Inc., a subsidiary of Ziff Davis, Inc. The company's headquarters is located in San Francisco's SoMa district and is headed by its former editor-in-chief, Peer Schneider. The IGN website was the brainchild of media entrepreneur Chris Anderson and launched on September 29, 1996. It focuses on games, films, anime, television, comics, technology, and other media. Originally a network of desktop websites, IGN is also distributed on mobile platforms, console programs on the Xbox and PlayStation, FireTV, Roku, and via YouTube, Twitch, Hulu, and Snapchat.")

        st.write("Originally, IGN was the flagship website of IGN Entertainment, a website which owned and operated several other websites oriented towards players' interests, games, and entertainment, such as Rotten Tomatoes, GameSpy, GameStats, VE3D, TeamXbox, Vault Network, FilePlanet, and AskMen. IGN was sold to publishing company Ziff Davis in February 2013 and operates as a J2 Global subsidiary.")
        
        
        # st.write(data.head())
       


    with tab2:

        with st.container():
            st.header("About Dataset")

            st.subheader("Column descriptions:")
            st.write("Title: This column contains the titles of video games.")
            st.write("Score: This column represents the score given to each game, on a scale of 1 to 10.")
            st.write("Score Phrase: This column provides a qualitative assessment of the game's score, such as 'Masterpiece', indicating exceptionally high praise.")
            st.write("Platform: This column indicates the platform or console on which the game was released, such as Lynx, Wii, Game Boy Color, Xbox 360, or PlayStation 3.")
            st.write("Genre: This column specifies the genre(s) of the game, such as Racing, Action, RPG (Role-Playing Game), or Action-Adventure.")
            st.write("Release Year: This column indicates the year in which the game was released.")
            st.write("Release Month: This column specifies the month of release.")
            st.write("Release Day: This column specifies the day of release.")

        st.divider()

        with st.expander('Data Preview'):
            st.dataframe(
                data_original,
                column_config ={
                    "release_year": st.column_config.NumberColumn(format="%d")
                }
            )

        
            

        with st.container(border=True):

            col1, col2 = st.columns(2)

            with col1:

                st.subheader("Dataset description")
                st.write("A brief statistical summary of the data.")
                st.write(data_original.describe())

            with col2:
                st.subheader("Dataset info")

                # Función para obtener la información del DataFrame como una cadena de texto
                def get_info_text(df):
                    # Capturar la salida de data.info()
                    buffer = StringIO()
                    df.info(buf=buffer)
                    info_str = buffer.getvalue()
                    buffer.close()
                    return info_str

                # Obtener la información del DataFrame como una cadena de texto
                info_str = get_info_text(data_original)
                st.write("Let's explore the data types contained in the columns and check for any null values.")
                with st.container(border=True):

                    st.text(info_str)
    with tab3:
            st.subheader("Dataset manipulation")
            st.write("As we can see in the previous tabs, the data contains null and erroneous values (such as games released in 1970). Therefore, we will delete these records for a better analysis. Additionally, we will remove the columns 'release_month' and 'release_day' as they are not relevant to our analysis.")
            st.code("data = data.query('release_year != 1970').drop(columns = ['release_month', 'release_day']).dropna()")
            st.write("Finally, we will add a new column that represents the ecosystem in which the games were released. This will help us identify exclusive titles for further analysis.")

            with st.expander('Final Dataset Preview'):
                st.dataframe(
                    data_platform,
                    column_config ={
                        "release_year": st.column_config.NumberColumn(format="%d")
                    }
                )
            
            
    



def show_dashboard1():

    tab1, tab2 = st.tabs(["Title analysis", "Platform Analysis"])

    with tab1:

        with st.container(border = True):

            col1, col2 = st.columns(2)
            with col1:

                # Crear el histograma con Plotly Express
                fig2 = px.histogram(data['release_year'], nbins=30, color_discrete_sequence=custom_colors)

                # Personalizar el diseño del histograma
                fig2.update_layout(
                    title='Title distribution by release year',
                    xaxis_title='Release Year',
                    yaxis_title='Frequency')
                # Mostrar el gráfico en Streamlit
                st.plotly_chart(fig2, use_container_width=True)

            with col2:

                # Gráfico de barras para la columna 'score_phrase'
                ##st.subheader("Bar Chart de Score Phrase")
            
                # Crear un gráfico de barras con Plotly
                fig1 = px.bar(data, x='score_phrase', title="Score phrase by genre", color_discrete_sequence=custom_colors)
                fig1.update_layout(
                    xaxis_title='Score phrase',
                    yaxis_title='Count')
                st.plotly_chart(fig1, use_container_width=True)




        with st.container(border = True):

            col_f,col3, col4 = st.columns([0.15,0.425,0.425])

            with col_f:

                options_genre = st.multiselect("Genre", count_data_filtered["genre"].unique())

                # Filtrar el DataFrame según el rango de fechas seleccionado
                #filtered_data = count_data_filtered[(count_data_filtered['release_year'] >= date_range[0]) & (count_data_filtered['release_year'] <= date_range[1])]

                if not options_genre:
                    filtered_data = count_data_filtered
                    filtered_data_boxplot = data_t10_genre
                else:
                    filtered_data = count_data_filtered[count_data_filtered["genre"].isin(options_genre)]
                    filtered_data_boxplot = data_t10_genre[data_t10_genre["genre"].isin(options_genre)]


            with col3:

                

                # Crear un gráfico de líneas con Plotly
                fig1 = px.line(filtered_data, x='release_year', y='count', color='genre', title="Top 10 Genre evolution over the years ", ##width= 600, height=450,
                               color_discrete_sequence=custom_colors)
                fig1.update_xaxes(title="Release Year")
                fig1.update_yaxes(title="Genre")
                fig1.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig1, use_container_width=True)

            with col4:

                # Crear un gráfico de boxplot con Plotly
                ##st.subheader("Boxplot de Score por Género")
                fig2 = px.box(filtered_data_boxplot, x='genre', y='score', title="Top 10 Genre score", color_discrete_sequence=custom_colors)
                fig2.update_layout(
                    xaxis_title='Genre',
                    yaxis_title='Score')
                st.plotly_chart(fig2, use_container_width=True )

    with tab2:
        with st.container():
            col1, col2 = st.columns(2)

            with col1:
                col3, col4 = st.columns([0.2 , 0.8])

                with col3:
                    platform_ms = st.multiselect("Platform filter", count_platform_t10)

                    if not platform_ms:
                        filtered_data_pf = data_platform[data_platform['platform'].isin(count_platform_t10)]
                        count_pf_filtered = count_data_filtered_pf
                    else:
                        filtered_data_pf= data_platform[data_platform['platform'].isin(platform_ms)]
                        count_pf_filtered = count_data_filtered_pf[count_data_filtered_pf['platform'].isin(platform_ms)]

                with col4:
                    # Crear un gráfico de barras con Plotly
                    fig_bar_pf = px.bar(filtered_data_pf, x='score_phrase',  color='platform', title="Top 10 Platform score phrase by genre",
                                        color_discrete_sequence=custom_colors)
                    
                    fig_bar_pf.update_layout(
                        xaxis_title='Score phrase',
                        yaxis_title='Count',
                        legend_title_text='Platform')
                    st.plotly_chart(fig_bar_pf, use_container_width=True)


            with col2:
                
                    
                fig_line= px.line(count_pf_filtered, x='release_year', y='count', color='platform', title="Evolution of top 10 Platform over the years",
                                  color_discrete_sequence=custom_colors)
                fig_line.update_xaxes(title="Release Year")
                fig_line.update_yaxes(title="Genre")
                
                fig_line.update_layout(xaxis_tickangle=-45,
                                       legend_title_text='Platform')
                st.plotly_chart(fig_line, use_container_width=True)

            

        


def show_dashboard_exclusivos():
    st.title("Exclusives Analysis")

    tab1_ex, tab2_ex= st.tabs(["General", "By System"])


    ##cont1 = st.container(border = True)
    ##cont2 = st.container(border = True)
    
    

    with tab1_ex:           

        with st.container(border = True):

            col_filtros,col1 = st.columns([0.15,0.8])

            with col_filtros:
                with st.container(border= True):
                    st.write("Filters:")
                    scorephrase_ms = st.multiselect("Score Phrase", data_exclusivos["score_phrase"].unique())
                    genre_ms = st.multiselect("Genre", data_exclusivos["genre"].unique())
                
                if not scorephrase_ms and not genre_ms:
                    filtered_data_ex = data_exclusivos

                elif scorephrase_ms and not genre_ms:
                    filtered_data_ex = data_exclusivos[data_exclusivos["score_phrase"].isin(scorephrase_ms)]

                elif not scorephrase_ms and genre_ms:
                    filtered_data_ex = data_exclusivos[data_exclusivos["genre"].isin(genre_ms)]

                else:
                    filtered_data_ex = data_exclusivos[data_exclusivos["score_phrase"].isin(scorephrase_ms) & data_exclusivos["genre"].isin(genre_ms)]

            with col1:
                with st.container(border=True):

                    col1_1, col1_2 = st.columns(2)

                    with col1_1:


                        frecuencia_categoria = filtered_data_ex['system'].value_counts()

                        # Pie Chart

                        ##st.header("Release Charts")

                        # Crear un DataFrame con los nombres y valores
                        df = pd.DataFrame({'names': frecuencia_categoria.index, 'values': frecuencia_categoria.values})

                        # Agregar una columna 'color' al DataFrame usando el diccionario exclusive_colors
                        df['color'] = df['names'].map(exclusive_colors)

                        # Crear el gráfico de pastel
                        figpie = px.pie(df, names='names', values='values', title="Proportion of exclusive games by brand",color='names', color_discrete_map={'Nintendo': 'red',
                                                                                                                                  'Sony Playstation' : 'blue',
                                                                                                                                  'Microsoft Xbox' : 'green'
                                                                                                                   })




                        ##figpie = px.pie(names=names, values=frecuencia_categoria.values, title="Pie chart", color_discrete_map=exclusive_colors)

                        

                        ## Show chart Pie
                    
                        st.plotly_chart(figpie, use_container_width=True)
                        

                    with col1_2:

                        ## st.subheader("Line de Score Phrase")

                        data_line_ex = filtered_data_ex.groupby(['release_year', 'system']).size().reset_index(name='count')
                        fig_line_ex = px.line(data_line_ex, x='release_year', y='count', color = 'system', title="Games released by brand over the years.", width= 600, height=450,
                                              color_discrete_map=exclusive_colors)
                        fig_line_ex.update_xaxes(title="Año de Lanzamiento")
                        fig_line_ex.update_yaxes(title="Género")
                        fig_line_ex.update_layout(xaxis_tickangle=-45)
                        st.plotly_chart(fig_line_ex, use_container_width=True)

                
                with st.container(border=True):

                    col2_1, col2_2 = st.columns(2)

                    with col2_1:

                        # BoxPlot score
                        

                        fig2 = px.box(filtered_data_ex, x='system', y='score', color='system',title="Game score by brand", width= 600, height=450,
                                      color_discrete_map=exclusive_colors)
                        
                        fig2.update_layout(showlegend=False)
                        st.plotly_chart(fig2, use_container_width=True)

                    with col2_2:

                        st.markdown("**Statistics of game score by brand**")
                        
                        # Realizar el agrupamiento por la variable 'X' y agregar columnas de estadísticas en base a la variable 'Y'
                        resultado = filtered_data_ex.groupby('system', as_index=True).agg({'score': ['mean', 'max', 'min', 'count']})

                        # Aplanar el DataFrame
                        resultado.columns = ['_'.join(col).strip() for col in resultado.columns.values]

                        # Mostrar el DataFrame
                        resultado = resultado.round(2)
                        st.write(resultado)


    with tab2_ex:
        with st.container(border = True):
            col_filtros2,col3, col4 = st.columns([0.15,0.425,0.425])

            with col_filtros2:
                with st.container(border= True):
                    st.write("Filters:")
                    system_ms = st.multiselect("System", data_exclusivos["system"].unique())

                    if not system_ms:
                        filtered_data_ex = data_exclusivos
                    else:
                        
                        filtered_data_ex = data_exclusivos[data_exclusivos["system"].isin(system_ms)]

                    frecuencia_categoria = filtered_data_ex['score_phrase'].value_counts()

                    

            with col3:

                ##st.subheader("Bar Chart de Score Phrase")

                figpie = px.pie(names=frecuencia_categoria.index, values=frecuencia_categoria.values , color_discrete_sequence=custom_colors)
                figpie.update_layout(
                    title='Proportion of score phrase')
                st.plotly_chart(figpie, use_container_width=True)

            with col4:
                fig1 = px.bar(filtered_data_ex, x='score_phrase', title="Score phrase by genre" , color_discrete_sequence=custom_colors)
                fig1.update_layout(
                    xaxis_title='Score phrase',
                    yaxis_title='Count')
                st.plotly_chart(fig1, use_container_width=True, width=800, height=600)
    
        






if __name__ == "__main__":
    main()
