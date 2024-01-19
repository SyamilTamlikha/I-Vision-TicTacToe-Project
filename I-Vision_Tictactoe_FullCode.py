import cv2
import mediapipe as mp
import time
import pyautogui
from cvzone.HandTrackingModule import HandDetector
import random


def is_index_over_button(index_tip, button_rect):
    x, y = index_tip
    x1, y1, x2, y2 = button_rect
    return x1 < x < x2 and y1 < y < y2

def point_inside_rectangle(point, rect):
    x, y = point
    x1, y1, x2, y2 = rect
    return x1 < x < x2 and y1 < y < y2

def draw_board(frame, board):
    cv2.line(frame, (100, 0), (100, 300), (255, 255, 255), 2)
    cv2.line(frame, (200, 0), (200, 300), (255, 255, 255), 2)
    cv2.line(frame, (0, 100), (300, 100), (255, 255, 255), 2)
    cv2.line(frame, (0, 200), (300, 200), (255, 255, 255), 2)

    for row in range(3):
        for col in range(3):
            if board[row][col] == 'X':
                draw_x(frame, row, col)
            elif board[row][col] == 'O':
                draw_o(frame, row, col)

def draw_x(frame, row, col):
    x_start = col * 100
    y_start = row * 100
    x_end = (col + 1) * 100
    y_end = (row + 1) * 100
    cv2.line(frame, (x_start, y_start), (x_end, y_end), (0, 0, 255), 2)
    cv2.line(frame, (x_start, y_end), (x_end, y_start), (0, 0, 255), 2)

def draw_o(frame, row, col):
    center_x = int((col + 0.5) * 100)
    center_y = int((row + 0.5) * 100)
    cv2.circle(frame, (center_x, center_y), 40, (0, 255, 0), 2)

def check_winner(board):
    for row in range(3):
        if board[row][0] == board[row][1] == board[row][2] and board[row][0] != '':
            return board[row][0], ((row, 0), (row, 1), (row, 2))
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] and board[0][col] != '':
            return board[0][col], ((0, col), (1, col), (2, col))
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] != '':
        return board[0][0], ((0, 0), (1, 1), (2, 2))
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] != '':
        return board[0][2], ((0, 2), (1, 1), (2, 0))
    return None, None

def draw_winning_line(frame, line):
    for (row, col) in line:
        x = col * 100 + 50
        y = row * 100 + 50
        cv2.circle(frame, (x, y), 5, (255, 255, 255), -1)

def make_computer_move(board):
    available_moves = [(i, j) for i in range(3) for j in range(3) if board[i][j] == '']
    if available_moves:
        return random.choice(available_moves)
    else:
        return None
    
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

cap = cv2.VideoCapture(0)

board = [['', '', ''], ['', '', ''], ['', '', '']]
current_player = 'X'
winner = None

reset_button_rect = (50, 350, 250, 400)  # Define the region for the reset button

detector = HandDetector(detectionCon=0.8)

# Define button rectangles for 2-player mode and computer mode
two_player_button_rect = (370, 290, 570, 340)
computer_mode_button_rect = (370, 370, 570, 420)

current_mode = "2 Player"  # Initial mode

while True:
    ret, frame = cap.read()
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)


    hands2, frame = detector.findHands(frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            index_tip = (
                int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * frame.shape[1]),
                int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * frame.shape[0])
            )
            thumb_tip = (
                int(hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x * frame.shape[1]),
                int(hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y * frame.shape[0])
            )

            distance = ((index_tip[0] - thumb_tip[0])**2 + (index_tip[1] - thumb_tip[1])**2)**0.5
            if distance < 30:
                if is_index_over_button(index_tip, reset_button_rect):
                    board = [['', '', ''], ['', '', ''], ['', '', '']]
                    winner = None
                elif is_index_over_button(index_tip, two_player_button_rect):
                    current_mode = "2 Player"
                elif is_index_over_button(index_tip, computer_mode_button_rect):
                    current_mode = "Computer"

                if current_mode == "2 Player" and not winner:
                    for row in range(3):
                        for col in range(3):
                            if board[row][col] == '':
                                x_center = col * 100 + 50
                                y_center = row * 100 + 50
                                if (
                                    index_tip[0] > x_center - 50
                                    and index_tip[0] < x_center + 50
                                    and index_tip[1] > y_center - 50
                                    and index_tip[1] < y_center + 50
                                ):
                                    board[row][col] = current_player
                                    winner, line = check_winner(board)
                                    if winner:
                                        print(f'Player {winner} wins!')
                                        draw_winning_line(frame, line)
                                    current_player = 'O' if current_player == 'X' else 'X'
                if current_mode == "Computer" and not winner:
                    if current_player == 'X':
                        for row in range(3):
                            for col in range(3):
                                if board[row][col] == '':
                                    x_center = col * 100 + 50
                                    y_center = row * 100 + 50
                                    if (
                                        hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * frame.shape[1] > x_center - 50
                                        and hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * frame.shape[1] < x_center + 50
                                        and hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * frame.shape[0] > y_center - 50
                                        and hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * frame.shape[0] < y_center + 50
                                    ):
                                        board[row][col] = current_player
                                        winner, line = check_winner(board)
                                        if winner:
                                            print(f'Player {winner} wins!')
                                            draw_winning_line(frame, line)
                                        current_player = 'O'
                    else:
                        computer_move = make_computer_move(board)
                        if computer_move:
                            row, col = computer_move
                            board[row][col] = current_player
                            winner, line = check_winner(board)
                            if winner:
                                print(f'Player {winner} wins!')
                                draw_winning_line(frame, line)
                            current_player = 'X'
                    
                    # Implement computer move logic here (e.g., random move)
                    # This will depend on how you want the computer to make moves

    draw_board(frame, board)

    # Display the winner at the top of the frame
    if winner:
        if winner == "O":
            B=0 
            G=255  
            R=0
        else:
            B=0 
            G=0  
            R=255
        cv2.putText(frame, f'Player {winner} wins!', (350, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (B, G, R), 2, cv2.LINE_AA)
        
    else:
        cv2.putText(frame, f'{current_mode} mode', (320, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
        
    # Display the reset button
    cv2.rectangle(frame, reset_button_rect[:2], reset_button_rect[2:], (0, 0, 255), cv2.FILLED)
    cv2.putText(frame, 'Reset', (90, 390), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

    # Display the 2-player mode button
    cv2.rectangle(frame, two_player_button_rect[:2], two_player_button_rect[2:], (255, 0, 0), cv2.FILLED)
    cv2.putText(frame, '2 Player', (400, 320), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

    # Display the computer mode button
    cv2.rectangle(frame, computer_mode_button_rect[:2], computer_mode_button_rect[2:], (255, 0, 0), cv2.FILLED)
    cv2.putText(frame, 'Computer', (400, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

    cv2.imshow('I-Vision TicTacToe', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()