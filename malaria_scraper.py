#!/usr/bin/env python3

import string
from io import StringIO
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
    :param df: country name, possibly followed by () and/or ;
    :return: mutated dataframe by trimming country name
    """
    # delete ( and following, escape (
    df['country'] = df['country'].str.replace(r'\(.*', '')
    # delete ; and following
    df['country'] = df['country'].str.replace(r';.*', '')
    df['country'] = df['country'].str.strip()
    return df


def get_dataframe(country_name_first_letter):

    # read from local data file
    filename = malaria_filename(country_name_first_letter)
    df = pd.read_html(filename)[0]

    df.columns = ['country', 'areas_with_malaria', 'estimated_risk', 'drug_resistance', 'malaria_species', 'rec_prophylaxis', 'info']
    df = df.drop(columns=['drug_resistance', 'malaria_species', 'rec_prophylaxis', 'info'])

    trim_country(df)

    df['estimated_risk'] = df['estimated_risk'].astype('category')

    return df


if __name__ == '__main__':

    # get_tables_write_files()

    df = get_dataframe('b')


