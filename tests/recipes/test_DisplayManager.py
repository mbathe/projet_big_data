import pytest
from unittest.mock import patch, MagicMock
from src.pages.recipes.Analyse_recipes import DisplayManager, DataManager
import pandas as pd
from datetime import date
import locale

# Créez un DataFrame factice pour les tests
dummy_data = pd.DataFrame({
    'name': ['Recipe1', 'Recipe2'],
    'submitted': [pd.Timestamp('2021-01-01'), pd.Timestamp('2021-02-01')],
    'nutrition': ["{'calories': 100}", "{'calories': 200}"],  
    'description': ['Delicious', 'Tasty'],
    'tags': [['vegan'], ['gluten-free']],
    'ingredients': ["['ingredient1', 'ingredient2']", "['ingredient3', 'ingredient4']"],  # Chaînes de caractères
    'n_steps': [3, 5],
    'minutes': [30, 45],
    'contributor_id': [1, 2]
})

# from src.process.recipes import Recipe

@pytest.fixture
def display_manager():
    with patch('src.utils.helper_data.load_dataset_from_file') as mock_load_dataset:
        mock_load_dataset.return_value = dummy_data
        with patch('src.pages.welcom.Welcom.Welcome.show_welcom') as mock_show_welcom:
            mock_show_welcom.return_value = dummy_data
            with patch('src.process.recipes.Recipe.detect_dataframe_anomalies') as mock_detect_anomalies:
                mock_detect_anomalies.return_value = {}
                with patch.object(DataManager, 'get_recipe_data') as mock_get_recipe_data:
                    # Créez un mock pour st.session_state.data
                    mock_session_state = MagicMock()
                    mock_session_state.data = dummy_data
                    # Assignez st.session_state au mock retourné par get_recipe_data
                    mock_get_recipe_data.return_value.st = MagicMock(session_state=mock_session_state)
                    
                    data_manager = DataManager()
                    display_manager = DisplayManager(data_manager=data_manager)
                    yield display_manager




def test_display_nutrition_analysis_exception(display_manager):
    with patch.object(display_manager.data_manager, 'analyze_nutrition', side_effect=Exception("Nutrition error")):
        with patch('logging.error') as mock_logging_error:
            display_manager.display_nutrition_analysis()
            mock_logging_error.assert_called_once_with("Error in display_nutrition_analysis: Nutrition error")


def test_display_steps_and_time_analysis_exception(display_manager):
    with patch.object(display_manager.data_manager, 'analyze_recipe_complexity', side_effect=Exception("Complexity error")):
        with patch('logging.error') as mock_logging_error:
            display_manager.display_steps_and_time_analysis()
            mock_logging_error.assert_called_once_with("Error in display_steps_and_time_analysis: Complexity error")


def test_display_steps_and_time_analysis_details(display_manager):
    with patch('streamlit.checkbox') as mock_checkbox:
        mock_checkbox.return_value = True  # Simulate checkbox is checked
        with patch('streamlit.dataframe') as mock_dataframe:
            display_manager.display_steps_and_time_analysis()
            assert mock_dataframe.call_count >= 1


def test_display_tags_analysis_exception(display_manager):
    with patch.object(display_manager.data_manager, 'analyze_tags', side_effect=Exception("Tags error")):
        with patch('logging.error') as mock_logging_error:
            display_manager.display_tags_analysis()
            mock_logging_error.assert_called_once_with("Error in display_tags_analysis: Tags error")



def test_display_distribution_histogram_exception(display_manager):
    with patch('numpy.random.lognormal', side_effect=Exception("Random error")):
        with patch('logging.error') as mock_logging_error:
            data = {
                'total_contributors': 1000,
                'contributions_per_user': {'mean': 10}
            }
            display_manager._display_distribution_histogram(data, 'blues')
            mock_logging_error.assert_called_once_with("Error in _display_distribution_histogram: Random error")


def test_display_contributors_analysis_exception(display_manager):
    with patch('streamlit.title', side_effect=Exception("Display error")):
        with patch('logging.error') as mock_logging_error:
            display_manager.display_contributors_analysis()
            mock_logging_error.assert_called_once_with("Error in display_contributors_analysis: Display error")



def test_sidebar_load_data(display_manager):
    with patch('streamlit.sidebar'), \
         patch('streamlit.date_input') as mock_date_input, \
         patch('streamlit.button') as mock_button, \
         patch('streamlit.success') as mock_success, \
         patch.object(DisplayManager, 'display_welcome_screen') as mock_welcome_screen:

        mock_date_input.return_value = (date(2021, 1, 1), date(2021, 12, 31))
        mock_button.return_value = True  # Simulate button click

        # Simulate that 'data' is not in session state
        display_manager.data_manager.get_recipe_data().st.session_state = {}

        display_manager.sidebar()

        mock_welcome_screen.assert_called_once()
        mock_success.assert_called_once_with("Période d'analyse: 2021-01-01 à 2021-12-31")



def test_display_welcome_screen_without_image(display_manager):
    with patch('src.pages.recipes.Analyse_recipes.DisplayManager.get_img_as_base64') as mock_get_img:
        mock_get_img.return_value = None
        with patch('streamlit.markdown') as mock_markdown:
            display_manager.display_welcome_screen()
            mock_markdown.assert_called()


def test_display_welcome_screen_with_image(display_manager):
    with patch('src.pages.recipes.Analyse_recipes.DisplayManager.get_img_as_base64') as mock_get_img:
        mock_get_img.return_value = 'image_base64_data'
        with patch('streamlit.markdown') as mock_markdown:
            display_manager.display_welcome_screen()
            mock_markdown.assert_called()
                   

def test_get_img_as_base64_exception(display_manager):
    with patch('builtins.open', side_effect=Exception("File not found")):
        with patch('streamlit.error') as mock_st_error:
            result = display_manager.get_img_as_base64("invalid/path.jpg")
            mock_st_error.assert_called_once_with("Erreur de chargement de l'image : File not found")
            assert result is None


def test_display_tab_exception(display_manager):
    with patch('streamlit.tabs', side_effect=Exception("Tabs error")):
        with patch('logging.error') as mock_logging_error:
            display_manager.display_tab()
            mock_logging_error.assert_called_once_with("Error in display_tab: Tabs error")


def test_display_anomalies_values_exception(display_manager):
    with patch('streamlit.checkbox', side_effect=Exception("Checkbox error")):
        with patch('logging.error') as mock_logging_error:
            display_manager.display_anomalies_values()
            mock_logging_error.assert_called_once_with("Error in display_anomalies_values: Checkbox error")


def test_display_data_structures_show_columns(display_manager):
    with patch('streamlit.checkbox') as mock_checkbox:
        mock_checkbox.return_value = True
        with patch('streamlit.write') as mock_write, \
             patch('streamlit.markdown') as mock_markdown, \
             patch('streamlit.table') as mock_table:
            display_manager.display_data_structures()
            mock_write.assert_called_once()
            mock_table.assert_called_once()


def test_display_data_structures_with_search(display_manager):
    with patch('streamlit.text_input') as mock_text_input:
        mock_text_input.return_value = 'Delicious'  # Simulate search term
        with patch('streamlit.dataframe') as mock_dataframe:
            display_manager.display_data_structures(columns_to_show=['name', 'description'], search_term='Delicious')
            mock_dataframe.assert_called_once()



def test_display_submission_analysis(display_manager):
    with patch('streamlit.slider') as mock_slider:
        mock_slider.side_effect = [2015, 2018]  # Simulate selecting years
        with patch('self.data_manager.analyze_temporal_distribution') as mock_analyze:
            mock_analyze.return_value = {
                'submissions_per_year': {2015: 100, 2016: 150, 2017: 200, 2018: 250},
                'submissions_per_month': {1: 50, 2: 60},
                'submissions_per_weekday': {0: 80, 1: 70}
            }
            display_manager.display_submission_analysis()
            # No assertions needed if code runs without errors



def test_display_comparative_analysis_exception(display_manager):
    with patch('plotly.graph_objects.Figure', side_effect=Exception("Radar chart error")):
        with patch('logging.error') as mock_logging_error:
            display_manager._display_comparative_analysis(pd.DataFrame(), {})
            mock_logging_error.assert_called_once_with("Error in _display_comparative_analysis: Radar chart error")


def test_display_top_contributors_exception(display_manager):
    with patch('streamlit.slider', side_effect=Exception("Slider error")):
        with patch('logging.error') as mock_logging_error:
            display_manager._display_top_contributors(pd.DataFrame(), 'blues')
            mock_logging_error.assert_called_once_with("Error in _display_top_contributors: Slider error")


def test_create_top_contributors_figure_exception(display_manager):
    with patch('plotly.express.bar', side_effect=Exception("Bar chart error")):
        with patch('logging.error') as mock_logging_error:
            display_manager._create_top_contributors_figure(pd.DataFrame(), 'blues')
            mock_logging_error.assert_called_once_with("Error in _create_top_contributors_figure: Bar chart error")


def test_create_distribution_figure_exception(display_manager):
    with patch('plotly.graph_objects.Figure', side_effect=Exception("Figure error")):
        with patch('logging.error') as mock_logging_error:
            display_manager._create_distribution_figure({})
            mock_logging_error.assert_called_once_with("Error in _create_distribution_figure: Figure error")


def test_analysis_tab_options(display_manager):
    options = [
        "Distribution des soumissions",
        "Analyse des Étapes et du Temps",
        "Analyse les informations nutritionnelles",
        "Analyse les tags des recettes",
        "Analyse les contributions par utilisateur"
    ]
    methods = [
        'display_submission_analysis',
        'display_steps_and_time_analysis',
        'display_nutrition_analysis',
        'display_tags_analysis',
        'display_contributors_analysis'
    ]

    for option, method in zip(options, methods):
        with patch('streamlit.selectbox') as mock_selectbox:
            mock_selectbox.return_value = option
            with patch.object(display_manager, method) as mock_method:
                display_manager.analysis_tab()
                mock_method.assert_called_once()


def test_home_tab_exception(display_manager):
    with patch('streamlit.title', side_effect=Exception("Error in home_tab")):
        with patch('logging.error') as mock_logging_error:
            display_manager.home_tab()
            mock_logging_error.assert_called_once_with("Error in home_tab: Error in home_tab")


def test_home_tab_metrics(display_manager):
    # Prepare mock data for annomalis["column_info"]
    display_manager.data_manager.get_recipe_data().annomalis = {
        "column_info": pd.DataFrame({
            'Unique Count': [100, 200],
            'Unique Percentage': [50, 75]
        }, index=['submitted', 'name'])
    }
    columns_to_show = ["name", "submitted"]

    with patch('streamlit.markdown') as mock_markdown:
        display_manager.home_tab()
        # Verify that st.markdown is called for both 'submitted' and 'name'
        assert mock_markdown.call_count == 2


def test_sidebar_clean_data(display_manager):
    with patch('streamlit.sidebar'), \
         patch('streamlit.toggle') as mock_toggle:

        mock_toggle.return_value = True  # Simulate toggle is on

        with patch.object(display_manager.data_manager.get_recipe_data(), 'clean_dataframe') as mock_clean:
            display_manager.sidebar()
            mock_clean.assert_called_once()


def test_sidebar_invalid_date_range(display_manager):
    with patch('streamlit.sidebar') as mock_sidebar, \
         patch('streamlit.date_input') as mock_date_input, \
         patch('streamlit.button') as mock_button, \
         patch('streamlit.error') as mock_error:

        # Simulate date input where start_date > end_date
        mock_date_input.return_value = (date(2021, 12, 31), date(2021, 1, 1))
        mock_button.return_value = True  # Simulate button click

        display_manager.sidebar()

        mock_error.assert_called_once_with("La date de début doit être antérieure ou égale à la date de fin.")


def test_load_css(display_manager):
    with patch('src.pages.recipes.Analyse_recipes.CSSLoader.load') as mock_load_css:
        display_manager.load_css()
        mock_load_css.assert_any_call('src/css_pages/analyse_user.css')
        mock_load_css.assert_any_call('src/css_pages/recipe.css')


def test_home_tab(display_manager):
    with patch('streamlit.title') as mock_title:
        display_manager.home_tab()
        mock_title.assert_called_once_with("🏠 Analyse de Recettes")


def test_analysis_tab(display_manager):
    with patch('streamlit.selectbox') as mock_selectbox:
        display_manager.analysis_tab()
        mock_selectbox.assert_called_once()


def test_display_contributors_analysis(display_manager):
    with patch('streamlit.title') as mock_title:
        display_manager.display_contributors_analysis()
        mock_title.assert_called_once_with("📊 Analyse des Contributions")


def test_display_tags_analysis(display_manager):
    with patch('streamlit.title') as mock_title:
        display_manager.display_tags_analysis()
        mock_title.assert_called_once_with("📊 Analyse des Tags de Recettes")


def test_display_submission_analysis(display_manager):
    with patch('streamlit.title') as mock_title:
        display_manager.display_submission_analysis()
        mock_title.assert_called_once_with("📊 Analyse des Soumissions")


def test_display_steps_and_time_analysis(display_manager):
    with patch('streamlit.title') as mock_title:
        display_manager.display_steps_and_time_analysis()
        mock_title.assert_called_once_with("📊 Analyse des Étapes et du Temps")



def test_display_nutrition_analysis(display_manager):
    with patch('streamlit.sidebar.header') as mock_title:
        display_manager.display_nutrition_analysis()
        mock_title.assert_called_once_with("Filtres Nutritionnels")

def test_display_data_structures(display_manager):
    with patch('streamlit.subheader') as mock_subheader:
        display_manager.display_data_structures()
        mock_subheader.assert_called_once_with(
            "Afficharger des 5 premiers elements du dataset")



def test_display_anomalies_values(display_manager):
    with patch('streamlit.checkbox') as mock_checkbox:
        display_manager.display_anomalies_values()
        mock_checkbox.assert_called_once_with("Afficher les valeurs abérantes")


def test_sidebar_exception(display_manager):
    # Mock streamlit components to raise an exception
    with patch('streamlit.sidebar') as mock_sidebar:
        mock_sidebar.__enter__.side_effect = Exception("Sidebar error")
        with patch('logging.error') as mock_logging_error:
            display_manager.sidebar()
            mock_logging_error.assert_called_once_with("Error in sidebar: Sidebar error")

def test_home_tab_description(display_manager):
    with patch('streamlit.selectbox') as mock_selectbox:
        mock_selectbox.return_value = "Description du dataset"
        display_manager.home_tab()
        # Assertions to verify Code block A is executed

def test_home_tab_ingredient(display_manager):
    with patch('streamlit.selectbox') as mock_selectbox:
        mock_selectbox.return_value = "Colonne Ingredient"
        display_manager.home_tab()
        # Assertions to verify Code block B is executed

def test_home_tab_description_column(display_manager):
    with patch('streamlit.selectbox') as mock_selectbox:
        mock_selectbox.return_value = "Colonne Description"
        display_manager.home_tab()
        # Assertions to verify Code block C is executed


def test_analyze_ingredients(display_manager):
    with patch('src.pages.recipes.Analyse_recipes.st.write') as mock_write, \
         patch('src.pages.recipes.Analyse_recipes.st.table') as mock_table, \
         patch('src.pages.recipes.Analyse_recipes.st.markdown') as mock_markdown, \
         patch('src.pages.recipes.Analyse_recipes.st_echarts') as mock_echarts:
        
        display_manager.analyze_ingredients()
        
        # Vérifiez que st.write a été appelé avec le bon message
        mock_write.assert_called_once_with("10 ingrédients les plus frequents dans les recettes")
        
        # Vérifiez que st.table a été appelé avec le DataFrame attendu
        mock_table.assert_called_once()
        
        # Vérifiez que st.markdown a été appelé avec le bon message
        mock_markdown.assert_called_once_with("### Nuage de mots")
        
        # Vérifiez que st_echarts a été appelé avec les options de nuage de mots
        mock_echarts.assert_called_once()
