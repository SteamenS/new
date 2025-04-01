import sys
from PyQt6.QtWidgets import QApplication, QMessageBox, QVBoxLayout, QTextEdit, QProgressBar, QRadioButton, QMainWindow, QCheckBox, QRadioButton
from random import shuffle
from PyQt6 import uic

class Question():
    def __init__(self, type, questionText, answersList, rightAnswer):
        self.type = type
        self.questionText = questionText
        self.answersList = answersList
        self.rightAnswer = rightAnswer

questions = [ #{type, question, answers, right_answers}
    Question(QRadioButton, '1?', [1,2,3,4], ['1']),
    Question(QCheckBox, '1,2,3?', [1,2,3,4], ['1','2','3']),
    Question(QTextEdit, 'Напиши 123', [''], ['123']),
    Question(QTextEdit, '2+2', [''], ['4']),
    Question(QCheckBox, '2-2', [0,4,6,8], ['0'])
]

class FinalWindow(QMainWindow):
    def __init__(self, parentWindow): 
        super().__init__() 
        self.parentWindow = parentWindow
        self.initUI() 
        
    def initUI(self):
        uic.loadUi('8quest2.ui', self)
        self.restartButton.hide()
        
        right = 0
        for answer in self.parentWindow.userAnswers:
            answer_index = None
            try:
                answer_index = self.parentWindow.rightAnswers.index(answer)
            except:
                answer_index = -1
                
            if answer_index != -1:
                right += 1
        
        rightPercentage = right/self.parentWindow.totalQuestions*100
        self.finalLabel.setText(f'Правильных ответов: [{right}/{self.parentWindow.totalQuestions}] ({rightPercentage}%)')
        
        self.finishButton.clicked.connect(self.finish)
        self.restartButton.clicked.connect(self.restart)
        
        if rightPercentage < 80:
            self.restartButton.show()
        
    def finish(self):
        self.parentWindow.show()
        self.hide()
        
    def restart(self):
        self.parentWindow.start()
        self.hide()

class QuestionWindow(QMainWindow):
    def __init__(self, parentWindow, question): 
        super().__init__() 
        self.parentWindow = parentWindow
        self.questionObject = question
        self.initUI() 
 
    def initUI(self):
        uic.loadUi('8quest.ui', self)
        
        self.progressBar: QProgressBar
        self.answerLayout_2: QVBoxLayout
        
        self.progressBar.setRange(0, self.parentWindow.totalQuestions)
        self.progressBar.setValue(self.parentWindow.curQuestion)
        
        self.questionCount.setText(f'{self.parentWindow.curQuestion}/{self.parentWindow.totalQuestions}')
        self.questionText.setText(f'{self.questionObject.questionText}')
        if self.parentWindow.curQuestion != self.parentWindow.totalQuestions:
            self.finishButton.hide()
        else:
            self.answerButton.hide()
        
        self.answerButtons = []
        for answerText in self.questionObject.answersList:
            answerObject = self.questionObject.type(self)
            self.answerLayout_2.addWidget(answerObject)
            answerObject.setText(str(answerText))
            self.answerButtons.append(answerObject)
        
        self.nextButton.triggered.connect(self.nextQuestion)
        self.prevButton.triggered.connect(self.prevQuestion)
        self.restartButton.triggered.connect(self.restart)
        self.exitButton.triggered.connect(self.exit)
        
        self.answerButton.clicked.connect(self.nextQuestion)
        self.finishButton.clicked.connect(self.finishQuest)
        
    def get_answer(self):
        answer = None
        if self.questionObject.type != QTextEdit:
            answer = []
            for i in self.answerButtons:
                if i.isChecked():
                    answer.append(i.text())
        else:
            answer = [str(self.answerButtons[0].toPlainText())]
        
        return answer
    
    def finishQuest(self):
        answer = self.get_answer()
        
        self.parentWindow.finish(answer)
    
    def nextQuestion(self):
        answer = self.get_answer()
        if answer == [''] or []:
            self._throw_error('Пожалуйста, хотя бы выберите ответ')
        elif self.parentWindow.curQuestion == self.parentWindow.totalQuestions:
            self._throw_error('Это уже конец теста!')
        else:
            self.parentWindow.next(answer)
        
    def prevQuestion(self):
        answer = self.get_answer()
        if self.parentWindow.curQuestion == 1:
            self._throw_error('Это уже самый первый вопрос!')
       
        self.parentWindow.prev(answer)
        
    def restart(self):
        self.parentWindow.start()
        
        self.hide()
        
    def exit(self):
        self.hide()
        self.parentWindow.show()
        
    def _throw_error(self, text):
        errorBox = QMessageBox()
        errorBox.setWindowTitle('Ошибка')
        errorBox.setText(text) 
        errorBox.setIcon(QMessageBox.Icon.Warning) 
        errorBox.setStandardButtons(QMessageBox.StandardButton.Ok)  
        errorBox.exec()
        
class MainWindow(QMainWindow): 
    def __init__(self): 
        super().__init__() 
        self.initUI() 
 
    def initUI(self):
        uic.loadUi('StartWindow8.ui', self)

        self.pushButton.clicked.connect(self.start)

    def start(self):
        self.questions = questions.copy()
        self.totalQuestions = len(self.questions)
        self.userAnswers = []
        
        self.questionWindows = []
        
        shuffle(self.questions)
        self.curQuestion = 1
            
        self.curQuestionWindow = QuestionWindow(self, self.questions[self.curQuestion-1])
        self.questionWindows.append(self.curQuestionWindow)
        self.curQuestionWindow.show()
        
        self.hide()
    
    def setAnswer(self, answer):
        try:
            self.userAnswers[self.curQuestion-1] = answer
        except:
            self.userAnswers.append(answer)
    
    def finish(self, curAnswer):
        self.curQuestionWindow.hide()
        self.setAnswer(curAnswer)
        
        self.rightAnswers = []
        for i in self.questions:
            self.rightAnswers.append(i.rightAnswer)
                
        self.finalWindow = FinalWindow(self)
        self.finalWindow.show()
    
    def next(self, curAnswer):
        self.curQuestionWindow.hide()
        self.setAnswer(curAnswer)
        if self.curQuestion == self.totalQuestions:
            pass
        else:
            self.curQuestion += 1
            try:
                self.curQuestionWindow = self.questionWindows[self.curQuestion-1]
                print('found1')
            except:
                self.curQuestionWindow = QuestionWindow(self, self.questions[self.curQuestion-1])
                self.questionWindows.append(self.curQuestionWindow)
                
            print(self.questionWindows)
            self.curQuestionWindow.show()
            
    def prev(self, answer):
        if self.curQuestion == 1:
            return
        
        try:
            self.userAnswers[self.curQuestion-1] = answer
        except:
            self.userAnswers.append(answer)
            
        self.curQuestionWindow.hide()
        self.curQuestion -= 1
        self.curQuestionWindow = self.questionWindows[self.curQuestion-1]
            
        self.curQuestionWindow.show()
        
if __name__ == '__main__':
    app = QApplication(sys.argv) 
    ex = MainWindow() 
    ex.show() 
    sys.exit(app.exec())    