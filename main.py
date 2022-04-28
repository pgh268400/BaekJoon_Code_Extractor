#!/usr/bin/env python
import os
import time

import requests
from bs4 import BeautifulSoup as bs

user_id = input("Enter Baekjoon ID : ")
judge_key = input("Enter Cookies/OnlineJudge : ")

# 초기 변수 설정
base_url = "https://www.acmicpc.net"  # 루트 도메인
url = f"https://www.acmicpc.net/status?user_id={user_id}&result_id=4"

cookie = {
    "OnlineJudge": judge_key
}
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
}


def get_next_page(url):
    try:
        s = requests.session()  # 세션 유지용
        req = s.get(url, cookies=cookie, headers=headers)
        soup = bs(req.text, "html.parser")
        next_page = soup.select_one("#next_page")['href']  # 다음 페이지 버튼
        result = base_url + next_page
        return result
    except Exception as e:  # 오류 발생시 다음페이지가 없는것으로 간주함.
        return False


def get_sorting(solve_num):
    source_url = "https://www.acmicpc.net/problem/" + solve_num
    req = s.get(source_url, cookies=cookie, headers=headers)
    soup = bs(req.text, "html.parser")
    sorting = soup.select("#problem_tags > ul > li > a")

    folder_name = ""
    separator = ", "  # 구분자

    for element in sorting:
        folder_name += element.get_text() + separator
    folder_name = folder_name.strip()[0:-1].strip()  # 맨 끝에 구분자 지우기
    return folder_name


def get_source(url):
    source_url = url

    req = s.get(source_url, cookies=cookie, headers=headers)
    soup = bs(req.text, "html.parser")
    source_code = soup.select_one("#source").get_text()  # 추출한 소스코드
    return source_code


def write_file(queue):
    # [정렬순서] 내림차순 :: 제출번호 -> 오름차순 :: 시간 -> 메모리
    sorted_queue = sorted(queue, key=lambda x: (-x[0], x[2], x[1]))
    save_num = None
    for edit_num, memory, timec, solve_num, language, source_code in sorted_queue:
        if solve_num == save_num:  # 번호가 겹침
            # 현재 Queue가 시간이 빠른것순으로 정렬되어 있으므로 시간복잡도가 빠른것만을 택하도록 한다. (메모리는 고려하지 않는다.)
            pass
        else:
            extension = ""
            if language == "Python 3" or language == "PyPy3":
                extension = "py"
            elif language == "C99":
                extension = "c"
            elif language.startswith("C++"):
                extension = "cpp"
            elif language.startswith("Java"):
                extension = "java"
            else:
                extension = "txt"  # 위 언어중에 없으면 txt로 저장함.

            download_folder = os.path.join("downloads", user_id)
            try:
                if not os.path.exists(download_folder):
                    os.makedirs(download_folder)
            except OSError:
                print('Error: Creating directory. ' + download_folder)
            file_path = os.path.join(download_folder, f"{solve_num}.{extension}")

            if os.path.isfile(file_path):
                print(f"{solve_num}번. 파일 중복으로 Pass 합니다.")
            else:
                f = open(file_path, 'w')
                f.write(source_code)
                f.close()
                print(f"{solve_num}번 처리 완료, 언어 {language}")
        save_num = solve_num


if __name__ == "__main__":
    s = requests.session()  # 세션 유지용
    while True:
        # 채점 현황 - 맞았습니다로 이동함.
        req = s.get(url, cookies=cookie, headers=headers)
        soup = bs(req.text, "html.parser")

        # 소스코드 추출 & 저장
        a_tag = soup.select('td > a:nth-child(2)')

        queue = []
        for element in a_tag:
            href = str(element['href'])  # 언어/수정 에서 언어부분은 무시하고 수정부분만 본다.
            if not "problem" in href:
                try:
                    # 문제 세부 사항 추출
                    solve_num = href.split("/")[2]  # 문제 번호
                    edit_num = href.split("/")[3]  # 수정번호 (제출 번호)
                    memory = soup.select_one(f"#solution-{edit_num} > td.memory").get_text()  # 메모리
                    timec = soup.select_one(f"#solution-{edit_num} > td.time").get_text()  # 시간
                    language = soup.select(f"#solution-{edit_num} > td > a:nth-child(1)")[1].get_text()  # 푼 언어

                    # 문제가 어디에 분류되어 있는지 추출
                    folder_name = get_sorting(solve_num)

                    # 소스코드 추출
                    source_code = get_source(base_url + href)  # 수정 버튼 누르면 나오는 url 제공

                    queue.append((int(edit_num), int(memory), int(timec), solve_num, language,
                                  source_code))  # queue에 처리할 것을 저장한다.
                    print(f"문제 {solve_num}번 추출 완료")
                except:
                    pass

                    # Queue에 있는것을 처리한다.
        write_file(queue)

        # 다음 페이지로 이동
        url = get_next_page(url)
        if url == False:
            break  # 다음페이지 없으면 반복 멈춤.
        time.sleep(0.5)  # 서버를 위한 delay
    print("처리가 완료 되었습니다.")
