import cv2

from math import pi, acos

from numpy import int0, uint8, array


class Answer:
    def __init__(self, image_path: str, number_of_questions: int):
        """
        image_path - absolute path to the image
        number_of_questions - number of questions
        """
        self.image_path = image_path
        self.image = cv2.imread(self.image_path)

        self.number_of_questions = number_of_questions

        self.check_image = None

        self.area = 2_600_000
        self.image_size = (1425, 1890)
        self.pixel_limit = 444

        if self.number_of_questions == 50:
            self._image_correction()
            self.student_id_image = self.image.copy()[265:635, 376:700]
            self.option_image = self.image.copy()[1372:1408, 428:644]
            self.answer_image_one = self.image.copy()[36:1886, 1142:1422]  # 1850 280
        elif self.number_of_questions == 100:
            self._image_correction()
            self.student_id_image = self.image.copy()[265:635, 186:510]  # 370 324
            self.option_image = self.image.copy()[1372:1408, 238:454]  # 36 216
            self.answer_image_one = self.image.copy()[36:1886, 800:1080]  # 1389 1142
            self.answer_image_two = self.image.copy()[36:1886, 1145:1422]

        self._option = None
        self._student_id = None
        self._list_of_answers = None

    def get_full_data(self) -> dict:
        """Get Data About Student Id, Option And Answers."""
        return {
            "id": self._student_id,
            "option": self._option,
            "answers": self._list_of_answers
        }

    def get_student_id(self) -> int:
        """Get Student Id."""
        return self._student_id

    def get_option(self) -> int:
        """Get Option."""
        return self._option

    def get_answers(self) -> list:
        """Get Answers."""
        return self._list_of_answers

    def student_id_main(self) -> None:
        """Find Student ID."""
        self.check_image = self.student_id_image

        answers_dict: dict = {
            1: "1",
            2: "2",
            3: "3",
            4: "4",
            5: "5",
            6: "6"
        }

        lst = self._find_coordinates_of_vertices(number_of_variation=6, number_of_sections=10)
        data = self._data_about_circle(question_list=lst)
        _student_id = self._check_data_from_circle_for_student_id(data, answers_dict)

        res = ["#", "#", "#", "#", "#", "#"]

        for i, elm in enumerate(_student_id):
            try:
                if isinstance(elm, list):
                    for j in elm:
                        index = int(j) - 1
                        res[index] = str(i) if res[index] == "#" else "*"
                else:
                    index = int(elm) - 1
                    res[index] = str(i) if res[index] == "#" else "&"
            except ValueError:
                pass

        try:
            self._student_id = int("".join(res))
        except ValueError:
            self._student_id = None

    def option_main(self) -> None:
        """Start Find Option."""
        self.check_image = self.option_image

        answers_dict: dict = {
            1: "1",
            2: "2",
            3: "3",
            4: "4",
        }

        lst = self._find_coordinates_of_vertices(number_of_variation=4, number_of_sections=1)
        data = self._data_about_circle(question_list=lst)
        result = self._check_data_from_circle(data, answers_dict)[0]

        if result in ('1', '2', '3', '4'):
            self._option = int(result)

    def answers_main(self) -> None:
        """Start Find Answers."""
        self.check_image = self.answer_image_one

        answers_dict = {
            1: "A",
            2: "B",
            3: "C",
            4: "D",
            5: "E"
        }

        lst = self._find_coordinates_of_vertices(number_of_variation=5, number_of_sections=50)
        data = self._data_about_circle(question_list=lst)

        if self.number_of_questions == 100:
            self.check_image = self.answer_image_two

            lst = self._find_coordinates_of_vertices(number_of_variation=5, number_of_sections=50)
            data += self._data_about_circle(question_list=lst)

        self._list_of_answers = self._check_data_from_circle(data, answers_dict)

    def _find_coordinates_of_vertices(self,
                                      number_of_variation: int,
                                      number_of_sections: int) -> list:
        """
        Построение координат и возвращение координат каждой секции
        number_of_variation => количество вариантов
        number_of_sections => количество секций
        """
        height = int(self.check_image.shape[0] / number_of_sections)
        width = int(self.check_image.shape[1] / number_of_variation)
        lst = list()

        for i in range(1, number_of_sections + 1):
            y = height * (i - 1)

            for j in range(number_of_variation):
                start_coordinate = (width * j, y)
                end_coordinate = (width * (j + 1), y + height)
                cv2.rectangle(img=self.check_image, pt1=start_coordinate, pt2=end_coordinate, color=(200, 200, 200),
                              thickness=2)
                lst.append((start_coordinate, end_coordinate))

        return [lst[i * number_of_variation: (i + 1) * number_of_variation] for i in range(number_of_sections)]

    def _data_about_circle(self, question_list: list) -> list:
        """Получение данных из секций."""
        data = list()

        for ans in question_list:
            lst = list()

            for elm in ans:
                a = 0

                for x in range(elm[0][0], elm[1][0]):
                    for y in range(elm[0][1], elm[1][1]):
                        if self.check_image[y, x] < 50:
                            a += 1

                lst.append(a)
            data.append(lst)

        return data

    def _check_data_from_circle(self, answers: list, answers_dict: dict) -> list:
        """Получение ответа из данных."""
        result = dict()

        for i, elm in enumerate(answers, 1):
            s = list(filter(lambda x: x > self.pixel_limit, elm))  # Выбор пикселей
            result[i] = answers_dict.get(elm.index(max(elm)) + 1)

            if len(s) >= 2:  # Проверка ответа на больше чем одного выбранного ответа
                result[i] = "Səfh"

            if not len(s):  # Проверка ответа на пустоту
                result[i] = "Boş"

        return list(result.values())

    def _check_data_from_circle_for_student_id(self, answers: list, answers_dict: dict) -> list:
        """Получение ответа из данных."""
        result = dict()

        for i, elm in enumerate(answers, 1):
            s = list(filter(lambda x: x > self.pixel_limit, elm))  # Выбор пикселей больше 690
            result[i] = answers_dict.get(elm.index(max(elm)) + 1)

            if len(s) >= 2:  # Проверка ответа на больше чем одного выбранного ответа
                result[i] = s
                for j, f in enumerate(s):
                    result[i][j] = answers_dict.get(elm.index(f) + 1)

            if not s:  # Проверка ответа на пустоту
                result[i] = "Boş"

        return list(result.values())

    def _rotate_image(self, angle):
        """Вращение изображения."""
        height, width = self.image.shape[:2]  # Высота и ширина
        point = width // 2, height // 2  # Точка вращения
        mat = cv2.getRotationMatrix2D(point, angle, 1)  # Матрица вращения

        return cv2.warpAffine(self.image, mat, (width, height))

    def _find_contours(self, thresh) -> tuple:
        """Нахождение прямоугольника."""
        # Нахождение всех контуров
        contours = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]

        # Нахождение максимальной площади
        max_area = max([int(cv2.minAreaRect(i)[1][0] * cv2.minAreaRect(i)[1][1]) for i in contours])

        # Перебираем все найденные контуры в цикле
        for cnt in contours:
            rect = cv2.minAreaRect(cnt)  # Пытаемся вписать прямоугольник
            area = int(rect[1][0] * rect[1][1])  # Вычисление площади

            # Выбор контура по площади
            if area > self.area and area == max_area:
                box = cv2.boxPoints(rect)  # Поиск четырех вершин прямоугольника
                box = int0(box)  # Округление координат

                # Вычисление координат двух векторов, являющихся сторонам прямоугольника
                edge1 = int0((box[1][0] - box[0][0], box[1][1] - box[0][1]))
                edge2 = int0((box[2][0] - box[1][0], box[2][1] - box[1][1]))

                # Выясняем какой вектор больше
                used_edge = edge1 if cv2.norm(edge1) > cv2.norm(edge2) else edge2

                # Вычисляем угол между самой длинной стороной прямоугольника и горизонтом
                angle = 180.0 / pi * acos(
                    (1 * used_edge[0] + 0 * used_edge[1]) / (cv2.norm((1, 0)) * cv2.norm(used_edge)))

                return angle, box

        raise ValueError("Don't find box!")

    def _image_correction(self) -> None:
        """Исправление изображения."""
        hsv_min = array((0, 0, 0), uint8)
        hsv_max = array((0, 0, 60), uint8)

        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.image = cv2.inRange(self.image, 185, 255)
        self.image = cv2.cvtColor(self.image, cv2.COLOR_GRAY2BGR)

        hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)  # меняем цветовую модель с BGR на HSV
        thresh = cv2.inRange(hsv, hsv_min, hsv_max)  # применяем цветовой фильтр

        angle, coordinate_box = self._find_contours(thresh)
        lst = list(sorted(coordinate_box, key=lambda x: sum(x)))
        angle = angle - 90 if lst[0][0] < lst[2][0] else 90 - angle

        if round(angle, 2) >= 0.1:
            self.image = self._rotate_image(angle)
            hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)  # меняем цветовую модель с BGR на HSV
            thresh = cv2.inRange(hsv, hsv_min, hsv_max)  # применяем цветовой фильтр
            _, coordinate_box = self._find_contours(thresh)
            lst = list(sorted(coordinate_box, key=lambda x: sum(x)))

        self.image = self.image[lst[0][1]:lst[2][1], lst[0][0]:lst[1][0]]
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

        self.image = cv2.resize(self.image, self.image_size)
