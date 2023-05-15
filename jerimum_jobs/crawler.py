import requests
from bs4 import BeautifulSoup
import re
from .job import Job
import json

domain = 'https://jerimumjobs.imd.ufrn.br'

def _get_soup(url:str):
    response = requests.get(url)
    if response.content: 
        content = response.content
        soup = BeautifulSoup(response.content, 'html.parser')
    else:
        raise Exception("Sorry, bad request {0}".format(response.status_code))
    
    soup = BeautifulSoup(content, 'html.parser')

    return soup

def crawlJobs(start_url='https://jerimumjobs.imd.ufrn.br/jerimumjobs/oportunidade/listar'):
    page = _get_soup(start_url)

    def get_jobs_by_category(page:BeautifulSoup):
        div = page.find('div', attrs={'class':'row', 
                                    'style':'position: sticky; top: 160px;'})
        jobs_by_category = div.find_all('li')

        return jobs_by_category

    def get_list_areas_jobs(jobs_by_category):
        list_areas_jobs = []
        for job_category in jobs_by_category:
            # filter area text
            area = job_category.find('a')
            area = area.text.strip()
            area = re.sub(r' \([0-9]+?\)', '', area)
            
            # filter link 
            link = job_category.find('a')
            link = domain + link['href']

            # making a obj
            dct = {
                'area' : area,
                'link' : link
            }
            list_areas_jobs.append(dct)

        return list_areas_jobs
    
    def get_jobs(list_areas_jobs:list[dict]):
        list_jobs = []

        def get_link_jobs(soup):
            list_divs = soup.find_all('div', attrs={'class':'row'})
            div = list_divs[4]
            links = div.find_all('a')
            
            return links            

        def _get_title(soup:BeautifulSoup):
            title = soup.find('h1')
            title = title.text.strip()

            return title

        def _get_description(soup:BeautifulSoup):
            header = soup.find('div', attrs={'class':'col'})
            # header = divs[2]
            description = header.text.replace('Descrição','').strip()

            return description

        def _get_salary(soup:BeautifulSoup):
            div = soup.find('div', attrs={'class':'col'})
            h5_tags = div.find_all('h5',attrs={'class':'d-inline text-nowrap mr-4'})
            if len(h5_tags) >=4:
                div_salary = h5_tags[3]
                salary = div_salary.find('span')
                salary = salary.text.strip()
                salary = salary.replace('.','')
                salary = re.sub(r',[0-9]{2}','',salary)
                salary = salary.replace('R$','').strip()
                try:
                    salary = int(float(salary))
                except:
                    salary = salary
            else:
                salary = None

            return salary

        for area_job in list_areas_jobs:
            soup = _get_soup(area_job['link'])
            links = get_link_jobs(soup)

            for link in links:
                soup = _get_soup(domain+link['href'])
                title = _get_title(soup)
                salary = _get_salary(soup)
                description = _get_description(soup)
                area = area_job['area']
                print(title)
                data = {
                    'title':title,
                    'salary':salary,
                    'description':description,
                    'area':area,
                }

                job = Job(data)
                list_jobs.append(job)

        return list_jobs

    def toJSON(dict):
        return json.dumps(dict, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

    def write_jobs(list_jobs):
        with open('./jobs.json', 'w') as file:
            # list_jobs = json.dumps(list_jobs)
            list_jobs = toJSON(list_jobs)
            file.write(list_jobs)
            # json.dump(list_jobs, file)

    jobs_by_category = get_jobs_by_category(page)
    list_areas_jobs = get_list_areas_jobs(jobs_by_category)
    list_jobs = get_jobs(list_areas_jobs)
    print(list_jobs)
    write_jobs(list_jobs)