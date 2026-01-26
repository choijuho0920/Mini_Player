import yt_dlp
import sys

def download_video(url):
    yt_opts = {
        # 1. 화질 설정: 최고 화질 비디오 + 최고 화질 오디오
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        
        # 2. 병합 포맷: mp4로 합치기 (FFmpeg 필요 - 설치 완료됨)
        'merge_output_format': 'mp4',
        
        # 3. 파일명 설정: '제목.확장자'로 저장
        'outtmpl': '%(title)s.%(ext)s',
        
        # 4. 후처리: mp4로 컨테이너 재정리
        'postprocessors': [{
            'key': 'FFmpegVideoRemuxer',
            'preferedformat': 'mp4',
        }],
    }
    
    try:
        print(f"\n[작업 시작] 정보를 불러오는 중입니다... : {url}")
        with yt_dlp.YoutubeDL(yt_opts) as ydl:
            ydl.download([url])
        print("\n[성공] 다운로드가 완료되었습니다!")
            
    except Exception as e:
        print(f"\n[오류] 문제가 발생했습니다: {e}")

def main():
    print("=== 유튜브 고화질 다운로더 (종료는 q) ===")
    while True:
        url = input('\n주소 입력 : ').strip()
        
        if url.lower() == 'q':
            print("프로그램을 종료합니다.")
            break
            
        if not url:
            continue
            
        download_video(url)

if __name__ == "__main__":
    main()