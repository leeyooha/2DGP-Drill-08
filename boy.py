from pico2d import load_image, get_time
from sdl2 import SDL_KEYDOWN, SDLK_RIGHT

from state_machine import StateMachine, space_down, time_out, right_down, left_up, left_down, right_up, start_event, auto_run_down

class Idle:
    @staticmethod
    def enter(boy, e):
        boy.dir = 0
        boy.frame = 0
        boy.action = 3  # 서있는 상태
        boy.start_time = get_time()

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)

class Sleep:
    @staticmethod
    def enter(boy, e):
        pass

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8

    @staticmethod
    def draw(boy):
        if boy.face_dir == 1:  # 오른쪽을 바라보며 눕기
            boy.image.clip_composite_draw(
                boy.frame * 100, 300, 100, 100,
                3.141592 / 2,  # 90도 회전
                '',  # 좌우 상하 반전 없음
                boy.x - 25, boy.y - 25, 100, 100
            )
        elif boy.face_dir == -1:  # 왼쪽을 바라보며 눕기
            boy.image.clip_composite_draw(
                boy.frame * 100, 200, 100, 100,
                -3.141592 / 2,  # 90도 회전
                '',  # 좌우 상하 반전 없음
                boy.x + 25, boy.y - 25, 100, 100
            )

class Run:
    @staticmethod
    def enter(boy, e):
        if right_down(e) or left_up(e):  # 오른쪽으로 달리기
            boy.dir, boy.action = 1, 1
        elif left_down(e) or right_up(e):  # 왼쪽으로 달리기
            boy.dir, boy.action = -1, 0

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy):
        boy.x += boy.dir * 5
        boy.frame = (boy.frame + 1) % 8

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)


# AutoRun 상태 추가
class AutoRun:
    @staticmethod
    def enter(boy, e):
        boy.dir = 1  # 기본적으로 오른쪽 방향으로 시작
        boy.speed = 10  # AutoRun 모드에서 속도를 높임
        boy.size_multiplier = 2  # 캐릭터 크기를 확대
        boy.start_time = get_time()  # AutoRun 시작 시간을 기록
        boy.action = 1 # 달리는 애니메이션

    @staticmethod
    def exit(boy, e):
        boy.speed = 5  # 속도를 정상으로 되돌림
        boy.size_multiplier = 1  # 캐릭터 크기를 정상으로 되돌림

    @staticmethod
    def do(boy):
        # 캐릭터를 자동으로 이동
        boy.x += boy.dir * boy.speed
        boy.frame = (boy.frame + 1) % 8
        # 화면 끝에 도달하면 방향 전환
        if boy.x < 50 or boy.x > 750:
            boy.dir *= -1
        # 5초 경과 후 Idle 상태로 복귀
        if get_time() - boy.start_time > 5:
            boy.state_machine.add_event(('TIME_OUT', 0))

    @staticmethod
    def draw(boy):
        width = int(100 * boy.size_multiplier)
        height = int(100 * boy.size_multiplier)
        flip = 'h' if boy.dir == -1 else ''

        boy.image.clip_composite_draw(
            boy.frame * 100, boy.action * 100, 100, 100,
            0, flip,  # 회전 없음, 반전 없음
            boy.x, boy.y, width, height
        )
class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.dir = 0
        self.action = 3

        self.image = load_image('animation_sheet.png')
        self.state_machine = StateMachine(self)  # 소년 객체의 state machine 생성
        self.state_machine.start(Idle)  # 초기 상태가 Idle
        # 상태 전환 테이블 설정에 AutoRun 상태와 전환 추가
        self.state_machine.set_transitions(
            {
                Idle: {right_down: Run, left_down: Run, left_up: Run, right_up: Run, auto_run_down: AutoRun, time_out: Sleep},  # AutoRun 상태로 전환 추가
                AutoRun: {time_out: Idle, right_down: Run, left_down: Run},  # AutoRun 상태에서 Idle, Run으로 전환 추가
                Sleep: {right_down: Run, left_down: Run, right_up: Run, left_up: Run, space_down: Idle},
                Run: {right_down: Idle, left_down: Idle, right_up: Idle, left_up: Idle}
            }
        )

    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        self.state_machine.add_event(('INPUT', event))

    def draw(self):
        self.state_machine.draw()
