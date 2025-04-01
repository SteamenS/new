import sys
from PyQt6.QtWidgets import QApplication, QMessageBox, QVBoxLayout, QProgressBar, QButtonGroup, QRadioButton, QMainWindow, QCheckBox, QLineEdit, QPushButton, QLabel, QWidget, QMenuBar

class Quest():
    checkButto = 'checkButto'    
    checkBo = 'checkBo' 
    Ntext = 'text'    


    def __init__(self, type, questionText, answersList, rightAnswer):
        self.type = type
        self.questionText = questionText
        self.answersList = answersList
        self.rightAnswer = rightAnswer

questions = [
    Quest(Quest.checkButto, 'Когда была первая отечественная война?', ['1812', '1816', '1814', '1337'], ['1812']),
    Quest(Quest.checkBo, 'Кто в ней участвовал?', ['Россия', 'Франция', 'Италия', 'Пруссия'], ['Россия', 'Франция', 'Италия', 'Пруссия']),
    Quest(Quest.Ntext, '2 = 2', [''], ['2']),
    Quest(Quest.checkButto, '1000 - 7', ['1337', '993', '-1', 'Danushka'], ['993']),
    Quest(Quest.checkBo, '1*2', ['1', '2', '3', '4'], ['1', '2'])
]

class QuestionWindow(QMainWindow):
    def __init__(self, question, parentWindow): 
        super().__init__()
        self.parentWindow = parentWindow
        self.questionObject = question
        self.initUI() 

    def initUI(self):
        self.setWindowTitle("Вопрос")
        self.setGeometry(100, 100, 400, 300)

        self.menuBar = QMenuBar(self)
        self.setMenuBar(self.menuBar)

        self.fileMenu = self.menuBar.addMenu("Меню")
        self.prevAction = self.fileMenu.addAction("Предыдущий вопрос")
        self.prevAction.triggered.connect(self.prev_question)

        self.nextAction = self.fileMenu.addAction("Следующий вопрос")
        self.nextAction.triggered.connect(self.nextQuestion)

        self.restartAction = self.fileMenu.addAction("Начать заново")
        self.restartAction.triggered.connect(self.restart_test)

        self.exitAction = self.fileMenu.addAction("Выход")
        self.exitAction.triggered.connect(self.close)

        self.layout = QVBoxLayout()
        self.questionLabel = QLabel(self.questionObject.questionText)
        self.layout.addWidget(self.questionLabel)

        self.progressBar = QProgressBar(self)
        self.layout.addWidget(self.progressBar)

        self.answerButtons = []
        if self.questionObject.type == Quest.checkButto:
            self.create_radio_buttons()
        elif self.questionObject.type == Quest.checkBo:
            self.create_checkboxes()
        elif self.questionObject.type == Quest.Ntext:
            self.create_text_input()

        self.submitButton = QPushButton("Ответить", self)
        self.submitButton.clicked.connect(self.nextQuestion)
        self.layout.addWidget(self.submitButton)

        self.setLayout(self.layout)
        self.setCentralWidget(QWidget(self))
        self.centralWidget().setLayout(self.layout)

        self.update_progress()

    def create_radio_buttons(self):
        self.button_group = QButtonGroup(self)
        for answer in self.questionObject.answersList:
            rb = QRadioButton(answer, self)
            self.layout.addWidget(rb)
            self.button_group.addButton(rb)
            self.answerButtons.append(rb)

    def create_checkboxes(self):
        for answer in self.questionObject.answersList:
            cb = QCheckBox(answer, self)
            self.layout.addWidget(cb)
            self.answerButtons.append(cb)

    def create_text_input(self):
        self.text_input = QLineEdit(self)
        self.layout.addWidget(self.text_input)
        self.answerButtons.append(self.text_input)

    def get_answer(self):
        if self.questionObject.type == Quest.checkButto:
            selected = self.button_group.checkedButton()
            return [selected.text()] if selected else []
        elif self.questionObject.type == Quest.checkBo:
            return [cb.text() for cb in self.answerButtons if isinstance(cb, QCheckBox) and cb.isChecked()]
        elif self.questionObject.type == Quest.Ntext:
            return [self.text_input.text()]
        return []

    def nextQuestion(self):
        answer = self.get_answer()
        if answer in ([], ['']):
            self._throw_error('Пожалуйста, выберите ответ')
        else:
            self.parentWindow.next(answer)

    def prev_question(self):
        if self.parentWindow.curQuestion > 1:
            self.parentWindow.curQuestion -= 1
            self.parentWindow.show_question()
        else:
            QMessageBox.warning(self, "Ошибка", "Это уже самый первый вопрос!")

    def restart_test(self):
        self.parentWindow.start()

    def _throw_error(self, text):
        errorBox = QMessageBox()
        errorBox.setWindowTitle('Ошибка')
        errorBox.setText(text) 
        errorBox.setIcon(QMessageBox.Icon.Warning) 
        errorBox.setStandardButtons(QMessageBox.StandardButton.Ok)  
        errorBox.exec()

    def update_progress(self):
        self.progressBar.setRange(0, self.parentWindow.totalQuestions)
        self.progressBar.setValue(self.parentWindow.curQuestion)

class MainWindow(QMainWindow): 
    def __init__(self): 
        super().__init__()
        self.initUI() 

    def initUI(self):
        self.setWindowTitle("Тестирование")
        self.setGeometry(100, 100, 300, 200)

        self.label = QLabel('Начать тестирование:', self)
        self.label.move(85, 35)
        self.label.resize(self.label.sizeHint()) 

        self.startButton = QPushButton("Начать", self)
        self.startButton.clicked.connect(self.start)
        self.startButton.move(90,100)

    def start(self):
        self.questions = questions.copy()
        self.totalQuestions = len(self.questions)
        self.userAnswers = []               
        self.curQuestion = 1                
        self.show_question()                 

    def setAnswer(self, answer):
        if len(self.userAnswers) < self.curQuestion:
            self.userAnswers.append(answer)
        else:
            self.userAnswers[self.curQuestion - 1] = answer

    def next(self, curAnswer):
        self.setAnswer(curAnswer)  
        if self.curQuestion < self.totalQuestions:
            self.curQuestion += 1
            self.show_question()   
        else:
            self.show_results() 

    def show_question(self):
        question = self.questions[self.curQuestion - 1]
        self.curQuestionWindow = QuestionWindow(question, self)
        self.curQuestionWindow.show()
        self.hide()

    def show_results(self):
        correct_answers = 0
        for i, question in enumerate(self.questions):
            if self.userAnswers[i] == question.rightAnswer:
                correct_answers += 1

        percentage = (correct_answers / self.totalQuestions) * 100
        result_message = f"Правильных ответов: {correct_answers}/{self.totalQuestions} ({percentage}%)"
        
        resultBox = QMessageBox()
        resultBox.setWindowTitle("Результаты")
        resultBox.setText(result_message)
        resultBox.setIcon(QMessageBox.Icon.Information)
        
        if percentage < 80:
            resultBox.setInformativeText("Тест не решен")
            resultBox.addButton("Заново", QMessageBox.ButtonRole.AcceptRole)
        else:
            resultBox.setInformativeText("Тест решен")
            resultBox.addButton("Конец", QMessageBox.ButtonRole.AcceptRole)

        resultBox.exec()
        self.start() 

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())