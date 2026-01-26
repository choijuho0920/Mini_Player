import tkinter as tk
from tkinter import ttk, messagebox, Scale, Menu
import vlc
import yt_dlp
import threading
import requests
import random
from PIL import Image, ImageTk
from io import BytesIO
import sys
import os

# --- 초기 설정 및 상수 ---

# VLC 라이브러리 체크
try:
    # vlc 인스턴스를 테스트 생성
    _test_instance = vlc.Instance()
    _test_instance.release()
except (ImportError, OSError, NameError):
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(
        "VLC 미설치 오류",
        "이 프로그램은 VLC Media Player(64bit)가 필요합니다.\n\n"
        "공식 홈페이지(videolan.org)에서 설치 후 다시 실행해주세요."
    )
    sys.exit(1)

# 색상 테마 설정
BG_NORMAL = "#FFFFFF"
FG_NORMAL = "#333333"

BG_SIMPLE = "#121212"
FG_SIMPLE_DEFAULT = "#E0E0E0"

# 심플 모드용 파스텔 톤
PASTEL_COLORS = [
    "#FFB7B2", "#FFDAC1", "#E2F0CB", "#B5EAD7", 
    "#C7CEEA", "#957DAD", "#89CFF0", "#FDFD96"
]

C_PLAY = "#B5EAD7"
C_NAV = "#F0F0F0"
C_SHUFFLE = "#FFDAC1"
C_REPEAT = "#E2F0CB"


class YouTubeAudioPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Mini Player")
        
        # 윈도우 닫기 이벤트 처리
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # 1. 창 초기 설정
        self.center_window(320, 520)
        self.root.resizable(False, False)
        self.root.configure(bg=BG_NORMAL)

        # 스타일 설정
        self.style_widgets()

        # 데이터 변수
        self.playlist = []
        self.current_index = -1
        self.is_minimal_mode = False
        self.is_dragging_time = False # 슬라이더 조작 중인지 여부
        self.repeat_mode = 0  # 0: None, 1: One, 2: All
        self.repeat_icons = ["🔁", "🔂", "➡"]
        self.repeat_colors = [C_REPEAT, "#FFD700", "#DDDDDD"]

        # VLC 초기화
        self.instance = vlc.Instance('--no-video', '--quiet')
        self.player = self.instance.media_player_new()
        self.events = self.player.event_manager()
        self.events.event_attach(vlc.EventType.MediaPlayerEndReached, self.on_song_finished)

        # GUI 구성
        self.setup_normal_gui()
        self.setup_minimal_gui()
        self.create_context_menu() # 우클릭 메뉴

        # 키/마우스 바인딩
        self.root.bind("<Escape>", lambda event: self.toggle_minimal_mode())
        
        # 드래그 변수
        self.drag_data = {"x": 0, "y": 0}
        
        # 업데이트 루프 시작
        self.update_progress_loop()

    def center_window(self, width, height):
        """화면 중앙에 창 배치"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def style_widgets(self):
        self.root.option_add("*Background", BG_NORMAL)
        self.root.option_add("*Button.relief", "flat")
        self.root.option_add("*Button.cursor", "hand2")
        self.root.option_add("*Listbox.relief", "flat")
        self.root.option_add("*Scale.highlightThickness", 0)

    # --- GUI Setup ---

    def create_context_menu(self):
        """우클릭 메뉴 (심플 모드에서 종료/전환 용이하게)"""
        self.context_menu = Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Toggle Mode (ESC)", command=self.toggle_minimal_mode)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Exit", command=self.on_close)
        
        # 윈도우 전체에 우클릭 바인딩
        self.root.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def setup_normal_gui(self):
        self.normal_frame = tk.Frame(self.root, bg=BG_NORMAL)
        self.normal_frame.pack(fill=tk.BOTH, expand=True)

        # 1. URL 입력
        input_box = tk.Frame(self.normal_frame, bg=BG_NORMAL, pady=10)
        input_box.pack(fill=tk.X, padx=15)
        
        self.url_entry = tk.Entry(input_box, bg="#F5F5F5", relief="flat", font=("Arial", 10))
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3)
        
        btn_add = tk.Button(input_box, text=" Add ", command=self.start_fetch_thread, bg="#333", fg="white", font=("Arial", 9, "bold"))
        btn_add.pack(side=tk.RIGHT, padx=(5, 0))

        # 2. 정보 영역 (썸네일 + 제목)
        self.info_area = tk.Frame(self.normal_frame, bg=BG_NORMAL)
        self.info_area.pack(fill=tk.BOTH, padx=15, pady=5)
        
        # 썸네일 표시용 라벨 (초기엔 빈 공간)
        self.thumb_label = tk.Label(self.info_area, bg="#FAFAFA", width=25, height=8, text="No Media", fg="#CCC")
        self.thumb_label.pack(pady=10, fill=tk.X)
        
        self.title_label = tk.Label(self.info_area, text="Ready to play", font=("Malgun Gothic", 11, "bold"), 
                                    wraplength=280, bg=BG_NORMAL, fg=FG_NORMAL)
        self.title_label.pack(pady=5)

        tk.Button(self.normal_frame, text="▼ Switch to Mini Player", command=self.toggle_minimal_mode, 
                  bg=BG_NORMAL, fg="#888", font=("Arial", 8)).pack()

        # 3. 진행 바
        progress_box = tk.Frame(self.normal_frame, bg=BG_NORMAL)
        progress_box.pack(fill=tk.X, padx=20, pady=10)
        
        self.lbl_cur = tk.Label(progress_box, text="00:00", font=("Arial", 8), fg="#888")
        self.lbl_cur.pack(side=tk.LEFT)
        
        self.time_scale = Scale(progress_box, from_=0, to=100, orient=tk.HORIZONTAL, showvalue=0, 
                                command=self.on_seek_drag, troughcolor="#F0F0F0", bg=BG_NORMAL, 
                                activebackground=C_PLAY, sliderlength=15, width=10)
        self.time_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)
        
        # [중요] 슬라이더 조작 시 튀는 현상 방지용 바인딩
        self.time_scale.bind("<ButtonPress-1>", self.on_slider_press)
        self.time_scale.bind("<ButtonRelease-1>", self.on_slider_release)

        self.lbl_tot = tk.Label(progress_box, text="00:00", font=("Arial", 8), fg="#888")
        self.lbl_tot.pack(side=tk.RIGHT)

        # 4. 컨트롤러
        ctrl_box = tk.Frame(self.normal_frame, bg=BG_NORMAL, pady=5)
        ctrl_box.pack()
        
        btn_cfg = {"width": 4, "pady": 5}
        tk.Button(ctrl_box, text="🔀", command=self.shuffle_playlist, bg=C_SHUFFLE, **btn_cfg).grid(row=0, column=0, padx=5)
        tk.Button(ctrl_box, text="⏮", command=self.play_prev, bg=C_NAV, **btn_cfg).grid(row=0, column=1, padx=5)
        
        self.btn_play = tk.Button(ctrl_box, text="▶", command=self.toggle_play_pause, bg=C_PLAY, width=8, font=("Arial", 12), pady=2)
        self.btn_play.grid(row=0, column=2, padx=5)
        
        tk.Button(ctrl_box, text="⏭", command=self.play_next, bg=C_NAV, **btn_cfg).grid(row=0, column=3, padx=5)
        
        self.btn_repeat = tk.Button(ctrl_box, text=self.repeat_icons[0], command=self.toggle_repeat, bg=self.repeat_colors[0], **btn_cfg)
        self.btn_repeat.grid(row=0, column=4, padx=5)

        # 볼륨
        vol_box = tk.Frame(self.normal_frame, bg=BG_NORMAL)
        vol_box.pack(pady=5)
        tk.Label(vol_box, text="Vol", font=("Arial", 8), fg="#999").pack(side=tk.LEFT)
        self.vol_scale = Scale(vol_box, from_=0, to=100, orient=tk.HORIZONTAL, command=self.set_volume, 
                               showvalue=0, length=100, width=8, bg=BG_NORMAL, troughcolor="#EEE")
        self.vol_scale.set(70)
        self.player.audio_set_volume(70)
        self.vol_scale.pack(side=tk.LEFT, padx=5)

        # 5. 리스트박스
        list_frame = tk.Frame(self.normal_frame, bg="#FAFAFA")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        scr = tk.Scrollbar(list_frame)
        scr.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.playlistbox = tk.Listbox(list_frame, yscrollcommand=scr.set, selectmode=tk.SINGLE, 
                                      bg="#FAFAFA", fg="#555", font=("Malgun Gothic", 9), 
                                      relief="flat", highlightthickness=0, selectbackground=C_PLAY, selectforeground="#333", activestyle="none")
        self.playlistbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.playlistbox.bind('<Double-1>', self.on_playlist_double_click)
        scr.config(command=self.playlistbox.yview)

    def setup_minimal_gui(self):
        self.minimal_frame = tk.Frame(self.root, bg=BG_SIMPLE)
        
        # 드래그 기능 바인딩
        self.minimal_frame.bind("<ButtonPress-1>", self.start_move)
        self.minimal_frame.bind("<ButtonRelease-1>", self.stop_move)
        self.minimal_frame.bind("<B1-Motion>", self.do_move)

        self.mini_title = tk.Label(self.minimal_frame, text="No Music", font=("Malgun Gothic", 10, "bold"), 
                                   bg=BG_SIMPLE, fg=FG_SIMPLE_DEFAULT)
        self.mini_title.pack(expand=True, fill=tk.BOTH)
        
        # 라벨 위에서도 드래그 가능하도록 바인딩
        self.mini_title.bind("<ButtonPress-1>", self.start_move)
        self.mini_title.bind("<ButtonRelease-1>", self.stop_move)
        self.mini_title.bind("<B1-Motion>", self.do_move)
        
        # 라벨 위에서도 우클릭 가능하도록
        self.mini_title.bind("<Button-3>", self.show_context_menu)

    # --- 기능 로직 ---

    def toggle_minimal_mode(self):
        if not self.is_minimal_mode:
            # -> 심플 모드 진입
            self.normal_frame.pack_forget()
            self.root.overrideredirect(True) # 타이틀바 제거
            self.root.geometry("300x40") 
            self.root.configure(bg=BG_SIMPLE)
            self.root.attributes("-topmost", True) # 항상 위에
            
            self.minimal_frame.pack(fill=tk.BOTH, expand=True)
            self.is_minimal_mode = True
            self.update_title_color()
        else:
            # -> 일반 모드 복귀
            self.minimal_frame.pack_forget()
            self.root.overrideredirect(False)
            self.root.geometry("320x520")
            self.root.configure(bg=BG_NORMAL)
            self.root.attributes("-topmost", False) # 항상 위에 해제
            
            self.normal_frame.pack(fill=tk.BOTH, expand=True)
            self.is_minimal_mode = False

    def update_title_color(self):
        if self.is_minimal_mode:
            self.mini_title.config(fg=random.choice(PASTEL_COLORS))
        else:
            self.title_label.config(fg=FG_NORMAL)

    def start_fetch_thread(self):
        url = self.url_entry.get().strip()
        if not url: return
        
        self.url_entry.delete(0, tk.END)
        self.title_label.config(text="Fetching info...", fg="#999")
        
        threading.Thread(target=self.fetch, args=(url,), daemon=True).start()

    def fetch(self, url):
        try:
            ydl_opts = {
                'quiet': True, 
                'extract_flat': True,
                'ignoreerrors': True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                added_count = 0
                if 'entries' in info:
                    for entry in info['entries']:
                        if entry:
                            self.add_song(entry)
                            added_count += 1
                else:
                    self.add_song(info)
                    added_count = 1

            self.root.after(0, lambda: self.title_label.config(text=f"Added {added_count} tracks", fg=FG_NORMAL))
            
            # 재생목록이 비어있었는데 추가됐다면 자동 재생
            if self.current_index == -1 and self.playlist:
                self.root.after(0, self.play_next)
                
        except Exception as e:
            print(e)
            self.root.after(0, lambda: self.title_label.config(text="Error fetching URL", fg="red"))

    def add_song(self, info):
        # 썸네일 URL 안전하게 가져오기
        thumb = info.get('thumbnails')[-1]['url'] if info.get('thumbnails') else None
        
        item = {
            'title': info.get('title', 'Unknown Title'),
            'url': info.get('url', info.get('webpage_url')),
            'thumb': thumb
        }
        self.playlist.append(item)
        self.root.after(0, lambda: self.playlistbox.insert(tk.END, item['title']))

    def play_track(self, idx):
        if not 0 <= idx < len(self.playlist): return
        
        self.player.stop()
        self.current_index = idx
        track = self.playlist[idx]

        # UI 업데이트
        self.title_label.config(text=track['title'])
        self.mini_title.config(text=track['title'])
        self.update_title_color()
        
        # 리스트박스 포커스 이동
        self.playlistbox.selection_clear(0, tk.END)
        self.playlistbox.selection_set(idx)
        self.playlistbox.see(idx)

        # 실제 재생을 위한 내부 쓰레드
        def _play_thread():
            try:
                # 오디오 스트림 URL 추출
                ydl_opts = {'format': 'bestaudio/best', 'quiet': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(track['url'], download=False)
                    play_url = info['url']
                    
                    media = self.instance.media_new(play_url)
                    self.player.set_media(media)
                    self.player.play()
                    
                    self.root.after(0, lambda: self.update_play_btn("||"))
                    
                    # 썸네일 업데이트
                    if track['thumb']:
                        self.update_thumbnail(track['thumb'])
            except Exception as e:
                print(f"Play Error: {e}")
                # 에러 시 다음 곡으로 넘기기 시도
                self.root.after(1000, self.play_next)

        threading.Thread(target=_play_thread, daemon=True).start()

    def update_thumbnail(self, url):
        try:
            res = requests.get(url, timeout=5)
            img_data = Image.open(BytesIO(res.content))
            
            # 비율 유지하며 리사이징
            img_data.thumbnail((250, 150), Image.Resampling.LANCZOS)
            img = ImageTk.PhotoImage(img_data)
            
            self.root.after(0, lambda: self._set_thumb_image(img))
        except:
            pass
            
    def _set_thumb_image(self, img):
        self.thumb_label.config(image=img, width=0, height=0) # 이미지 있으면 크기 자동
        self.thumb_label.image = img

    def toggle_play_pause(self):
        if self.player.is_playing():
            self.player.pause()
            self.update_play_btn("▶")
        else:
            if self.current_index == -1 and self.playlist:
                self.play_track(0)
            else:
                self.player.play()
                self.update_play_btn("||")

    def update_play_btn(self, text):
        self.btn_play.config(text=text)

    def play_prev(self):
        # 3초 이상 재생 중이면 처음으로, 아니면 이전 곡
        if self.player.get_time() > 3000:
            self.player.set_time(0)
        else:
            prev_idx = (self.current_index - 1 + len(self.playlist)) % len(self.playlist)
            self.play_track(prev_idx)

    def play_next(self):
        if not self.playlist: return
        
        # 한 곡 반복 모드
        if self.repeat_mode == 1:
            self.play_track(self.current_index)
            return

        next_idx = self.current_index + 1
        
        # 마지막 곡일 때
        if next_idx >= len(self.playlist):
            if self.repeat_mode == 0: # 반복 없음
                self.player.stop()
                self.update_play_btn("▶")
                return
            else: # 전체 반복
                next_idx = 0
        
        self.play_track(next_idx)

    def on_song_finished(self, event):
        self.root.after(100, self.play_next)

    # --- 반복 / 셔플 ---
    def toggle_repeat(self):
        self.repeat_mode = (self.repeat_mode + 1) % 3
        self.btn_repeat.config(text=self.repeat_icons[self.repeat_mode], bg=self.repeat_colors[self.repeat_mode])

    def shuffle_playlist(self):
        if not self.playlist: return
        
        current_url = self.playlist[self.current_index]['url'] if self.current_index != -1 else None
        random.shuffle(self.playlist)
        
        # 리스트박스 갱신
        self.playlistbox.delete(0, tk.END)
        for song in self.playlist:
            self.playlistbox.insert(tk.END, song['title'])
            
        # 현재 재생 중인 곡의 인덱스 찾아 업데이트
        if current_url:
            for i, song in enumerate(self.playlist):
                if song['url'] == current_url:
                    self.current_index = i
                    self.playlistbox.selection_set(i)
                    self.playlistbox.see(i)
                    break
        messagebox.showinfo("Shuffle", "Playlist Shuffled!")

    # --- 볼륨 및 슬라이더 ---
    def set_volume(self, val):
        self.player.audio_set_volume(int(val))

    def update_progress_loop(self):
        # 재생 중이고, 사용자가 슬라이더를 잡고 있지 않을 때만 업데이트
        if self.player.is_playing() and not self.is_dragging_time:
            cur = self.player.get_time()
            tot = self.player.get_length()
            
            if tot > 0:
                self.time_scale.config(to=tot)
                self.time_scale.set(cur)
                
                cur_str = f"{int(cur/60000):02}:{int((cur/1000)%60):02}"
                tot_str = f"{int(tot/60000):02}:{int((tot/1000)%60):02}"
                
                self.lbl_cur.config(text=cur_str)
                self.lbl_tot.config(text=tot_str)
                
        self.root.after(500, self.update_progress_loop)

    def on_seek_drag(self, val):
        # 드래그 중에는 라벨만 업데이트 (실제 이동은 release 시)
        time_ms = float(val)
        cur_str = f"{int(time_ms/60000):02}:{int((time_ms/1000)%60):02}"
        self.lbl_cur.config(text=cur_str)

    def on_slider_press(self, event):
        self.is_dragging_time = True

    def on_slider_release(self, event):
        target_time = int(self.time_scale.get())
        self.player.set_time(target_time)
        # 잠시 후 플래그 해제 (VLC 반응 시간 고려)
        self.root.after(200, lambda: setattr(self, 'is_dragging_time', False))

    def on_playlist_double_click(self, event):
        if self.playlistbox.curselection():
            self.play_track(self.playlistbox.curselection()[0])

    # --- 윈도우 이동 로직 (심플 모드용) ---
    def start_move(self, event):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def stop_move(self, event):
        self.drag_data["x"] = None
        self.drag_data["y"] = None

    def do_move(self, event):
        if self.is_minimal_mode and self.drag_data["x"] is not None:
            deltax = event.x - self.drag_data["x"]
            deltay = event.y - self.drag_data["y"]
            x = self.root.winfo_x() + deltax
            y = self.root.winfo_y() + deltay
            self.root.geometry(f"+{x}+{y}")

    def on_close(self):
        self.player.stop()
        self.root.destroy()
        sys.exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeAudioPlayer(root)
    root.mainloop()