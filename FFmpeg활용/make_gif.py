import subprocess
import os
import sys

def create_gif(video_path, start_time, duration, width=480, fps=10):
    """
    video_path: 원본 영상 파일 경로
    start_time: 시작 시간 (예: 00:01:23)
    duration: 지속 시간 (초 단위, 예: 3)
    width: 움짤 가로 크기 (세로는 비율에 맞춰 자동)
    fps: 초당 프레임 수 (GIF는 10~15 추천)
    """
    
    # 1. 파일 이름과 확장자 분리
    filename, _ = os.path.splitext(video_path)
    output_gif = f"{filename}_umzzal.gif"

    print(f"\n[작업 시작] '{output_gif}' 만드는 중...")
    
    # 2. FFmpeg 명령어 구성
    # -i: 입력 파일
    # -ss: 시작 시간
    # -t: 지속 시간
    # -vf: 비디오 필터 (fps 설정 + 크기 조절)
    # split [a][b]; ... : 화질 개선을 위한 팔레트 생성 (고화질 옵션)
    
    # 간단 버전 명령어 (화질은 보통, 속도는 빠름)
    cmd = [
        'ffmpeg',
        '-y',                 # 덮어쓰기 허용
        '-i', video_path,     # 원본 파일
        '-ss', start_time,    # 시작 시점
        '-t', str(duration),  # 길이
        '-vf', f'fps={fps},scale={width}:-1:flags=lanczos', # 프레임 및 크기 조정
        output_gif            # 결과 파일명
    ]

    try:
        # 명령어 실행 (터미널 출력 숨김)
        subprocess.run(cmd, check=True)
        print(f"✅ 완성! 파일이 생성되었습니다: {output_gif}")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 오류 발생: {e}")
    except FileNotFoundError:
        print("❌ FFmpeg를 찾을 수 없습니다. 설치가 잘 되었는지 확인해주세요.")

if __name__ == "__main__":
    print("=== 동영상 -> GIF 변환기 ===")
    
    # 1. 파일 경로 입력
    target_video = input("영상 파일 경로(또는 이름)를 입력하세요: ").strip().strip('"') # 따옴표 제거
    
    if not os.path.exists(target_video):
        print("파일을 찾을 수 없습니다!")
        sys.exit()

    # 2. 시간 설정
    start = input("시작 시간 (예: 00:00:10): ").strip()
    secs = input("몇 초간 만들까요? (예: 3): ").strip()
    
    # 3. 변환 실행
    create_gif(target_video, start, float(secs))