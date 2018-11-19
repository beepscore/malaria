#!/usr/bin/env python3

import string
import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import pandas as pd

"""
references
browsy scraper.py
https://github.com/beepscore/browsy

websearcher browser_driver.py
https://github.com/beepscore/websearcher
"""


def malaria_url(country_name_first_letter):
    """
    return url
    """
    base_url = 'https://www.cdc.gov/malaria/travelers/country_table'

    url_string = base_url + '/' + country_name_first_letter + '.html'
    return url_string


def malaria_filename(country_name_first_letter):
    """
    return filename
    """
    return './data/' + country_name_first_letter + '.html'


def get_table_html(country_name_first_letter):
    """
    Uses browser to request info.
    Waits for javascript to run and return html. Selects by css_id.
    :param country_name_first_letter: e.g. 'a'
    return table html. return empty string if timeout or error
    """
    # browser = webdriver.Firefox()
    browser = webdriver.Chrome()

    url = malaria_url(country_name_first_letter)
    browser.get(url)

    table_tag = 'table'

    try:
        # http://stackoverflow.com/questions/37422832/waiting-for-a-page-to-load-in-selenium-firefox-w-python?lq=1
        # http://stackoverflow.com/questions/5868439/wait-for-page-load-in-selenium
        WebDriverWait(browser, 6).until(lambda d: d.find_element_by_tag_name(table_tag).is_displayed())
        element = browser.find_element_by_tag_name(table_tag)
        return element.get_attribute('outerHTML')

    except TimeoutException:
        print("TimeoutException, returning empty string")
        return ""

    except AttributeError:
        # http://stackoverflow.com/questions/9823936/python-how-do-i-know-what-type-of-exception-occured#9824050
        print("AttributeError, returning empty string")
        return ""

    finally:
        browser.quit()


def get_tables_write_files():

    for letter in string.ascii_lowercase:
        text = get_table_html(letter)
        out_filename = malaria_filename(letter)

        with open(out_filename, 'w') as out_file:
            out_file.write(text)


def trim_country(df):
    """
    :param df: dataframe with column 'country' containing country name, possibly followed by () and/or ;
    :return: mutated dataframe by trimming country name
    """
    # delete ( and following, escape (
    df['country'] = df['country'].str.replace(r'\(.*', '')

    # delete ; and following
    df['country'] = df['country'].str.replace(r';.*', '')

    # delete , and following. For example change Bahamas, The to Bahamas
    df['country'] = df['country'].str.replace(r',.*', '')

    df['country'] = df['country'].str.strip()
    return df


def categorize_estimated_risk(df):
    """
    :param df: dataframe with column 'estimated_risk' containing risk, possibly followed by digit for footnote
               original data may contain string 'None', different from python object None
    :return: mutated dataframe by trimming estimated_risk and converting from string to category
    """
    # delete digit and following. For example in Afghanistan change Moderate2 to Moderate
    df['estimated_risk'] = df['estimated_risk'].str.replace(r'\d.*', '')

    df['estimated_risk'] = df['estimated_risk'].str.strip()

    # make case consistent e.g. original data may contain 'Very Low' and 'Very low'
    df['estimated_risk'] = df['estimated_risk'].str.lower()

    df['estimated_risk'] = df['estimated_risk'].astype('category')

    return df


def get_dataframe(country_name_first_letter):

    # read from local data file
    filename = malaria_filename(country_name_first_letter)

    if os.path.getsize(filename) == 0:
        # file is empty
        # avoid ValueError: No text parsed from document: ./data/x.html
        return pd.DataFrame()

    df = pd.read_html(filename)[0]

    df.columns = ['country', 'areas_with_malaria', 'estimated_risk', 'drug_resistance', 'malaria_species', 'rec_prophylaxis', 'info']
    df = df.drop(columns=['drug_resistance', 'malaria_species', 'rec_prophylaxis', 'info'])

    trim_country(df)

    categorize_estimated_risk(df)

    return df


def df_by_merging_iso_a3(df):
    """
    Adds column with iso three letter country abbreviation.
    For a given country, the name wording/spelling may vary
    but the iso 3 abbreviation is consistent.
    :param df: dataframe with column 'country' containing country name
    :return: dataframe by merging df_iso_a3 into df
    """

    df_iso_a3 = pd.read_csv('./data/iso_a3.csv')
    # print(len(df_iso_a3))
    # 177

    df = pd.merge(df, df_iso_a3, how='left')
    df = df.sort_values('iso_a3')
    # print(len(df))
    # 241

    # move country name to index
    df = df.set_index('country')

    # rename ivory coast
    df = df.rename({'CÃ´te dâIvoire': "Côte d'Ivoire"})

    # In column iso_a3 for rows missing value, add value.
    # https://en.wikipedia.org/wiki/ISO_3166-1
    # Fixed most countries with moderate or high risk.
    # TODO: Consider fixing more missing values

    df.loc['Andorra', 'iso_a3'] = 'AND'
    df.loc['Bahrain', 'iso_a3'] = 'BHR'
    df.loc['Burma', 'iso_a3'] = 'MMR'
    df.loc['Cape Verde', 'iso_a3'] = 'CPV'
    df.loc['Central African Republic', 'iso_a3'] = 'CAF'
    df.loc["Côte d'Ivoire", 'iso_a3'] = 'CIV'

    df.loc['Democratic Republic of the Congo', 'iso_a3'] = 'COD'
    df.loc['Dominican Republic', 'iso_a3'] = 'DOM'
    df.loc['Equatorial Guinea', 'iso_a3'] = 'GNQ'
    df.loc['French Guiana', 'iso_a3'] = 'GUF'
    df.loc['Laos', 'iso_a3'] = 'LAO'
    df.loc['Solomon Islands', 'iso_a3'] = 'SLB'
    df.loc['South Korea', 'iso_a3'] = 'ROK'
    df.loc['South Sudan', 'iso_a3'] = 'SSD'

    # virgin islands have 2 entries British VGB and United States VIR
    # TODO: assign each row correctly
    df.loc['Virgin Islands', 'iso_a3'] = 'VGB'

    df.reset_index()

    return df


def get_dataframe_all_countries():

    df_all_letters = pd.DataFrame()

    for letter in string.ascii_lowercase:
        df_letter = get_dataframe(letter)
        df_all_letters = df_all_letters.append(df_letter)

    df_all_letters = df_by_merging_iso_a3(df_all_letters)

    return df_all_letters


if __name__ == '__main__':

    pd.set_option('display.max_columns', 6)
    pd.set_option('display.max_rows', 200)

    # only need to write files once
    # get_tables_write_files()

    df = get_dataframe_all_countries()
    # print(len(df))
    # 241

    print(df)


