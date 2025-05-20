import time

import pyautogui

from src.custom_logger import dpi_logger

MASK = 0x3F


def build_alphabet(bitmask: int) -> str:
    alphabet = ''
    if bitmask & (1 << 0):
        alphabet += '0123456789'
    if bitmask & (1 << 1):
        alphabet += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if bitmask & (1 << 2):
        alphabet += "abcdefghijklmnopqrstuvwxyz"
    if bitmask & (1 << 3):
        alphabet += 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
    if bitmask & (1 << 4):
        alphabet += 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    if bitmask & (1 << 5):
        alphabet += '!@#$%^&*()-_=+[]{}|;:\'",.<>/?`~'
    return alphabet


def try_password(password: str) -> bool:
    pass


def focus_target_window():
    time.sleep(3)
    pyautogui.click()
    time.sleep(0.5)
    pyautogui.press('tab')
    time.sleep(0.1)
    pyautogui.press('tab')
    time.sleep(0.3)


def hack_pass():
    alpha = build_alphabet(MASK)
    alpha_len = len(alpha)

    pass_length = 1
    indexes_list = [0] * pass_length
    attempts = 0

    start_time = time.time()
    while True:
        forged_pass = ''
        for index in indexes_list:
            forged_pass = forged_pass.join(alpha[index])

        if attempts % 100000 == 0:
            elapsed = time.time() - start_time
            dpi_logger.debug(f"[{attempts}] Trying: {forged_pass} | Elapsed: {elapsed:.2f}s")

        attempts += 1
        if try_password(forged_pass):
            elapsed = time.time() - start_time
            avg = elapsed / attempts
            dpi_logger.info(f"Password hacked: {forged_pass}")
            dpi_logger.info(f"Total attempts: {attempts}")
            dpi_logger.info(f"Total time: {elapsed:.2f} s")
            dpi_logger.info(f"Avg time per attempt: {avg:.5f} s")
            return

        # Iterate through each symbol of alphabet, until pass len limit
        curr_pos = pass_length - 1
        while curr_pos >= 0:
            # If index represents last symb in alpha, then switch to next pos, else increment index on this pos
            if (indexes_list[curr_pos] + 1) < alpha_len:
                indexes_list[curr_pos] += 1
                break
            else:
                indexes_list[curr_pos] = 0
                curr_pos -= 1

        # Increment password len and do again
        else:
            pass_length += 1
            indexes_list = [0] * pass_length
