from abc import ABC, abstractmethod

import requests

from config import HH_URL, SJ_URL, API_SJ
from src.vacancy import Vacancy


class APImanager(ABC):
    """Класс для работы с API сторонних сервисов"""

    @abstractmethod
    def get_vacancies(self):
        """Получает вакансии со стороннего ресурса"""
        pass

    @abstractmethod
    def format_data(self):
        """Форматирует данные, полученные по API в единый формат"""


class HeadHunterApi(APImanager):
    """Класс для работы с сайтом hh.ru"""

    def __init__(self, keyword):
        """
        Инициализатор класса.
        :param keyword: ключевое слово для создания запроса
        """
        self.keyword = keyword

    def get_vacancies(self):
        """
        Получает ваканасии со стороннего ресурса hh.ru
        :return: список вакансий в json файле
        """
        response = requests.get(HH_URL, headers={"User-Agent": "HH-User-Agent"}, params={'text': self.keyword})
        return response.json()

    def format_data(self):
        """
        Форматирует данные, полученные по API в единый формат
        :return: Список вакансий в едином формате
        """
        hh_formatted_vacancies = []
        hh_data = self.get_vacancies()
        for vac in hh_data['items']:
            try:
                vacancy_info = {
                    'name_vacancy': vac.get('name'),
                    'url': vac.get('alternate_url'),
                    'requirements': vac.get('snippet').get('requirements'),
                    'employer': vac.get('employer').get('name'),
                    'city': vac.get('area').get('name'),
                    'salary_from': vac['salary'].get('from') if vac['salary'] else 0,
                    'salary_to': vac['salary'].get('to') if vac['salary'] else 0
                }
            except (KeyError, TypeError, IndexError, ValueError):
                print("Информации по заданным параметрам не найдено")

            # создание экземпляра класса с созданием полей из словаря (распаковка словаря)
            vacancy = Vacancy(**vacancy_info)
            vacancy.validate_data()
            hh_formatted_vacancies.append(vacancy)
        # список из объектов класса Vacancy
        return hh_formatted_vacancies


class SuperJobApi(APImanager):
    """Класс для работы с площадкой SuperJob.ru"""

    def __init__(self, keyword):
        """Инициализатор класса.
        :param keyword: ключевое слово для создания запроса
        """
        self.keyword = keyword

    def get_vacancies(self):
        """
        Получает ваканасии со стороннего ресурса SuperJob.ru
        :return: список вакансий в json файле
        """
        headers = {'X-Api-App-Id': API_SJ}
        response = requests.get(SJ_URL, headers=headers, params={'keyword': self.keyword})
        print(response.status_code)
        return response.json()

    def format_data(self):
        """
        Форматирует данные, полученные по API в единый формат
        :return: Список вакансий в едином формате
        """
        sj_formatted_vacancies = []
        sj_data = self.get_vacancies()
        for vac in sj_data['objects']:
            try:
                vacancy_info = {
                    'name_vacancy': vac.get('profession'),
                    'url': vac.get('link'),
                    'requirements': vac.get('candidat'),
                    'employer': vac.get('firm_name'),
                    'city': vac.get('town').get('title'),
                    'salary_from': vac['payment_from'] if vac['payment_from'] else 0,
                    'salary_to': vac['payment_to'] if vac['payment_to'] else 0
                }
            except (KeyError, TypeError, IndexError, ValueError):
                print("Информации по заданным параметрам не найдено")

            # создание экземпляра класса с созданием полей из словаря (распаковка словаря)
            vacancy = Vacancy(**vacancy_info)
            vacancy.validate_data()
            sj_formatted_vacancies.append(vacancy)
        # список из объектов класса Vacancy
        return sj_formatted_vacancies
