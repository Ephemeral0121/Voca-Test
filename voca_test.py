import sys
import random
import re
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QRadioButton, QMessageBox, QFileDialog, QLineEdit, QHBoxLayout
from PyQt5.QtGui import QFont

class QuizApp(QWidget):
    def __init__(self):
        super().__init__()
        self.data = []
        self.total_questions = 0
        self.answered_questions = 0
        self.correct_answers = 0
        self.choices = []  # 'choices' 속성 초기화
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.layout.setSpacing(20)

        # 파일로드 버튼
        self.load_button = QPushButton('Load File', self)
        self.load_button.setFont(QFont('Arial', 16))
        self.load_button.clicked.connect(self.load_file)
        self.layout.addWidget(self.load_button)

        # 단어 카운트 라벨
        self.word_count_label = QLabel('Word Count: 0')
        self.word_count_label.setFont(QFont('Arial', 16))
        self.layout.addWidget(self.word_count_label)

        # 질문 카운트 라벨
        self.question_count_layout = QHBoxLayout()
        self.question_count_label = QLabel('Number of Questions:')
        self.question_count_label.setFont(QFont('Arial', 16))
        self.question_count_input = QLineEdit(self)
        self.question_count_input.setFont(QFont('Arial', 16))
        self.question_count_layout.addWidget(self.question_count_label)
        self.question_count_layout.addWidget(self.question_count_input)
        self.layout.addLayout(self.question_count_layout)

        # 시작버튼
        self.start_button = QPushButton('Start Quiz', self)
        self.start_button.setFont(QFont('Arial', 16))
        self.start_button.clicked.connect(self.start_quiz)
        self.layout.addWidget(self.start_button)

        # 질문 라벨
        self.question_label = QLabel(self)
        self.question_label.setFont(QFont('Arial', 18, QFont.Bold))
        self.layout.addWidget(self.question_label)


        self.radio_buttons = [QRadioButton(self) for _ in range(5)]  # 5개의 라디오 버튼 생성
        for i, radio_button in enumerate(self.radio_buttons):
            radio_button.toggled.connect(lambda checked, idx=i: self.on_radio_button_toggled(checked, idx))
            self.layout.addWidget(radio_button)

        # 정답 버튼
        self.submit_button = QPushButton('Check Answer', self)
        self.submit_button.setFont(QFont('Arial', 16))
        self.submit_button.clicked.connect(self.check_answer)
        self.layout.addWidget(self.submit_button)

        # 다음 질문 버튼
        self.next_button = QPushButton('Next Question', self)
        self.next_button.setFont(QFont('Arial', 16))
        self.next_button.clicked.connect(self.next_question)
        self.layout.addWidget(self.next_button)


        self.setLayout(self.layout)
        self.setGeometry(300, 300, 600, 400)
        self.setWindowTitle('Word Translation Quiz')
        self.setStyleSheet("QWidget { background-color: #f0f0f0 }"
                           "QPushButton { background-color: #a0a0a0; border: none; padding: 10px; font-size: 18px; }"
                           "QPushButton:hover { background-color: #c0c0c0 }"
                           "QLabel { color: #333333; font-size: 28px; }"
                           "QRadioButton { color: #333333; font-size: 23px; }"
                           "QLineEdit { border: 1px solid #a0a0a0; font-size: 18px; }")
        self.center()
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QApplication.desktop().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def load_file(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', '/home')
        if fname[0]:
            self.data = self.load_data_from_file(fname[0])
            self.word_count_label.setText(f'Word Count: {len(self.data)}')

    def start_quiz(self):
        try:
            self.total_questions = int(self.question_count_input.text())
            self.answered_questions = 0
            self.correct_answers = 0
            if self.total_questions > len(self.data) or self.total_questions <= 0:
                QMessageBox.warning(self, 'Error', 'Invalid number of questions.')
                return
            self.next_question()
        except ValueError:
            QMessageBox.warning(self, 'Error', 'Please enter a valid number.')

    def next_question(self):
            
        self.current_question, self.choices, self.correct_answer = self.generate_quiz()

        # 기존 라디오 버튼 제거
        for radio_button in self.radio_buttons:
            self.layout.removeWidget(radio_button)
            radio_button.deleteLater()

        # 새 질문에 대한 라디오 버튼 생성
        self.radio_buttons = [QRadioButton(option, self) for option in self.choices]

        # 'Check Answer' 버튼 위치 찾기
        check_answer_button_index = self.layout.indexOf(self.submit_button)
        
        # 라디오 버튼을 'Check Answer' 버튼 위치에 추가
        for radio_button in self.radio_buttons:
            self.layout.insertWidget(check_answer_button_index, radio_button)
            check_answer_button_index += 1  # 버튼을 추가할 때마다 인덱스 증가

        # 'Check Answer' 및 'Next' 버튼을 레이아웃에 다시 추가
        self.layout.insertWidget(check_answer_button_index, self.submit_button)
        self.layout.addWidget(self.next_button)

        if self.answered_questions >= self.total_questions:
            accuracy = (self.correct_answers / self.total_questions) * 100
            QMessageBox.information(self, 'Quiz Finished', f'You have completed the quiz.\nCorrect Answers: {self.correct_answers}/{self.total_questions}\nAccuracy: {accuracy:.2f}%')
            return

        self.current_question, self.choices, self.correct_answer = self.generate_quiz()
        self.question_label.setText(f"{self.current_question}")
        for i, option in enumerate(self.choices):
            self.radio_buttons[i].setText(option)
            self.radio_buttons[i].show()

        self.answered_questions += 1
        self.submit_button.setEnabled(True)
        self.question_label.setStyleSheet('color: black')
        

    def check_answer(self):
        selected_answer = None
        for radio_button in self.radio_buttons:
            if radio_button.isChecked():
                selected_answer = radio_button.text()
                break

        if selected_answer == self.correct_answer:
            self.correct_answers += 1
            self.question_label.setText(f'{self.current_question} Correct!')
            self.question_label.setStyleSheet('color: green')
        else:
            self.question_label.setText(f'Incorrect! \nCorrect answer: {self.correct_answer}')
            self.question_label.setStyleSheet('color: red')

        self.submit_button.setDisabled(True)


    def reset_question_label(self):
        self.question_label.setText('')
        self.question_label.setStyleSheet('color: black')

    def reset_radio_buttons(self):
        for radio_button in self.radio_buttons:
            radio_button.setChecked(False)
            radio_button.show()

    def generate_quiz(self):
        correct_question = random.choice(self.data)
        english_word, correct_translation = correct_question

        other_questions = [q for q in self.data if q[0] != english_word]
        random.shuffle(other_questions)

        choices = [correct_translation] + [q[1] for q in other_questions[:4]]
        random.shuffle(choices)

        return english_word, choices, correct_translation

    def load_data_from_file(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        data = []
        for line in lines:
            match = re.match(r"([a-zA-Z\s]+)(.+)", line.strip())
            if match:
                english_phrase, translation = match.groups()
                data.append((english_phrase.strip(), translation.strip()))
        return data

def main():
    app = QApplication(sys.argv)
    ex = QuizApp()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
