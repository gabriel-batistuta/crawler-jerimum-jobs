class Job:
    def __init__(self, data:dict):
        self.title = data['title']
        if data['salary'] == None:
            self.salary = 'Desconhecido'
        else:
            self.salary = data['salary']
        self.description = data['description']
        self.area = data['area']