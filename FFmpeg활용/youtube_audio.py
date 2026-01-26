import yt_dlp
import sys

def download_audio(url):
    # 오디오 다운로드 전용 설정
    yt_opts = {
        # 1. 가장 좋은 음질의 소스(webm 등)를 가져옴
        'format': 'bestaudio/best',
        
        # 2. 다운로드 후 FFmpeg를 이용해 MP3로 변환
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',       # mp3, m4a, wav 등 변경 가능
            'preferredquality': '192',     # 비트레이트 (192k = 고음질)
        }],
        
        # 3. 파일 이름 설정 (제목.mp3)
        'outtmpl': '%(title)s.%(ext)s',
    }
    
    try:
        print(f"\n[작업 시작] 오디오 정보를 불러오는 중입니다... : {url}")
        with yt_dlp.YoutubeDL(yt_opts) as ydl:
            ydl.download([url])
        print("\n[성공] MP3 변환 및 저장이 완료되었습니다!")
            
    except Exception as e:
        print(f"\n[오류] 문제가 발생했습니다: {e}")

def main():
    print("=== 유튜브 오디오(MP3) 다운로더 (종료는 q) ===")
    
    while True:
        url = input('\n주소 입력 : ').strip()
        
        # 'q' 또는 'Q' 입력 시 종료
        if url.lower() == 'q':
            print("프로그램을 종료합니다.")
            break
            
        if not url:
            continue
            
        download_audio(url)

if __name__ == "__main__":
    main()