import tkinter as tk
from tkinter import ttk, messagebox, Scale
import vlc
import yt_dlp
import threading
import requests
import random
from PIL import Image, ImageTk
from io import BytesIO

import sys
import ctypes
import os

# VLC 감지 및 안내 기능
try:
    import vlc
    # vlc 인스턴스를 한번 생성해봐서 실제로 작동하는지 테스트
    instance = vlc.Instance()
    instance.release()
except (ImportError, OSError, NameError):
    import tkinter as tk
    from tkinter import messagebox
    
    # 숨겨진 윈도우 생성 (메시지박스만 띄우기 위해)
    root = tk.Tk()
    root.withdraw() 
    
    messagebox.showerror(
        "VLC 미설치 오류", 
        "이 프로그램은 VLC Media Player가 필요합니다.\n\n"
        "공식 홈페이지(videolan.org)에서 VLC를 설치한 후\n"
        "다시 실행해주세요."
    )
    sys.exit(1) # 프로그램 종료
    
# --- 색상 설정 ---
# [일반 모드] 화이트 & 깔끔함
BG_NORMAL = "#FFFFFF"       
FG_NORMAL = "#333333" # 제목 잘 보이게 진한 회색

# [심플 모드] 다크 & 감성
BG_SIMPLE = "#121212" # 리얼 블랙에 가까운 다크
FG_SIMPLE_DEFAULT = "#E0E0E0"

# 랜덤 파스텔 색상 (심플 모드용)
PASTEL_COLORS = [
    "#FFB7B2", # Pink
    "#FFDAC1", # Peach
    "#E2F0CB", # Green
    "#B5EAD7", # Mint
    "#C7CEEA", # Lavender
    "#957DAD", # Purple
    "#89CFF0", # Baby Blue
    "#FDFD96", # Pastel Yellow
]

# 버튼 포인트 색상
C_PLAY = "#B5EAD7"   
C_NAV = "#E0E0E0"    
C_SHUFFLE = "#FFDAC1" 
C_REPEAT = "#E2F0CB"  

class YouTubeAudioPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Mini Player")
        
        # 1. 일반 모드 초기 설정
        self.root.geometry("320x520") 
        self.root.resizable(False, False) 
        self.root.configure(bg=BG_NORMAL)
        
        self.style_widgets()

        # 데이터
        self.playlist = []
        self.current_index = -1
        self.is_minimal_mode = False
        self.is_dragging_time = False
        self.repeat_mode = 0 
        self.repeat_icons = ["🔁", "🔂", "➡"]
        self.repeat_colors = [C_REPEAT, "#FFD700", "#F0F0F0"]

        # VLC 초기화
        self.instance = vlc.Instance('--no-video')
        self.player = self.instance.media_player_new()
        self.events = self.player.event_manager()
        self.events.event_attach(vlc.EventType.MediaPlayerEndReached, self.on_song_finished)

        # GUI 구성
        self.setup_normal_gui()
        self.setup_minimal_gui()

        self.set_volume(50)
        
        # [핵심] ESC 키 바인딩 (유일한 복귀 수단)
        self.root.bind("<Escape>", lambda event: self.toggle_minimal_mode())

        # 드래그 이동 (창 전체, 라벨 등 어디를 잡아도 이동 가능하게)
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.bind_drag_events(self.root)

        self.update_progress_loop()

    def style_widgets(self):
        self.root.option_add("*Background", BG_NORMAL)
        self.root.option_add("*Button.relief", "flat")
        self.root.option_add("*Button.cursor", "hand2")
        self.root.option_add("*Listbox.relief", "flat")
        self.root.option_add("*Scale.highlightThickness", 0)

    def bind_drag_events(self, widget):
        """위젯에 드래그 이동 기능 부여"""
        widget.bind("<ButtonPress-1>", self.start_move)
        widget.bind("<ButtonRelease-1>", self.stop_move)
        widget.bind("<B1-Motion>", self.do_move)

    def setup_normal_gui(self):
        self.normal_frame = tk.Frame(self.root, bg=BG_NORMAL)
        self.normal_frame.pack(fill=tk.BOTH, expand=True)

        # 1. 상단 입력
        input_box = tk.Frame(self.normal_frame, bg=BG_NORMAL, pady=5)
        input_box.pack(fill=tk.X, padx=10, pady=5)
        self.url_entry = tk.Entry(input_box, bg="#F0F0F0", width=20, relief="flat", font=("Arial", 9))
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        tk.Button(input_box, text="+", command=self.start_fetch_thread, bg="#EEE", width=3).pack(side=tk.RIGHT)

        # 2. 앨범아트 & 정보
        self.info_area = tk.Frame(self.normal_frame, bg=BG_NORMAL)
        self.info_area.pack(fill=tk.BOTH, padx=10)
        
        self.thumb_label = tk.Label(self.info_area, bg=BG_NORMAL)
        self.thumb_label.pack(pady=5)
        
        # [일반 모드] 제목: 진한 회색 (잘 보이게)
        self.title_label = tk.Label(self.info_area, text="No Song", font=("Malgun Gothic", 10, "bold"), 
                                    wraplength=300, bg=BG_NORMAL, fg=FG_NORMAL)
        self.title_label.pack(pady=5)

        # 모드 전환 안내
        tk.Button(self.normal_frame, text="Switch to Minimal (ESC to return)", command=self.toggle_minimal_mode, 
                  bg=BG_NORMAL, fg="#999", font=("Arial", 7), activebackground=BG_NORMAL).pack(pady=2)

        # 3. 재생 바
        progress_box = tk.Frame(self.normal_frame, bg=BG_NORMAL)
        progress_box.pack(fill=tk.X, padx=15, pady=5)
        self.lbl_cur = tk.Label(progress_box, text="00:00", font=("Arial", 7), fg="#999")
        self.lbl_cur.pack(side=tk.LEFT)
        self.time_scale = Scale(progress_box, from_=0, to=100, orient=tk.HORIZONTAL, showvalue=0, 
                                command=self.on_seek_drag, troughcolor="#EEE", bg=BG_NORMAL, activebackground=C_PLAY, sliderlength=15)
        self.time_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)
        self.lbl_tot = tk.Label(progress_box, text="00:00", font=("Arial", 7), fg="#999")
        self.lbl_tot.pack(side=tk.RIGHT)

        # 4. 컨트롤 버튼
        ctrl_box = tk.Frame(self.normal_frame, bg=BG_NORMAL, pady=5)
        ctrl_box.pack()
        
        tk.Button(ctrl_box, text="🔀", command=self.shuffle_playlist, bg=C_SHUFFLE, width=3).grid(row=0, column=0, padx=3)
        tk.Button(ctrl_box, text="⏮", command=self.play_prev, bg=C_NAV, width=4).grid(row=0, column=1, padx=3)
        self.btn_play = tk.Button(ctrl_box, text="▶", command=self.toggle_play_pause, bg=C_PLAY, width=6, font=("Arial", 11, "bold"))
        self.btn_play.grid(row=0, column=2, padx=3)
        tk.Button(ctrl_box, text="⏭", command=self.play_next, bg=C_NAV, width=4).grid(row=0, column=3, padx=3)
        self.btn_repeat = tk.Button(ctrl_box, text=self.repeat_icons[0], command=self.toggle_repeat, bg=self.repeat_colors[0], width=3)
        self.btn_repeat.grid(row=0, column=4, padx=3)

        # 볼륨
        vol_box = tk.Frame(self.normal_frame, bg=BG_NORMAL)
        vol_box.pack(pady=2)
        self.vol_scale = Scale(vol_box, from_=0, to=100, orient=tk.HORIZONTAL, command=self.set_volume, showvalue=0, length=80, width=8, bg=BG_NORMAL)
        self.vol_scale.set(50)
        self.vol_scale.pack()

        # 5. 재생목록
        list_box_frame = tk.Frame(self.normal_frame, bg=BG_NORMAL)
        list_box_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        scr = tk.Scrollbar(list_box_frame, width=10) 
        scr.pack(side=tk.RIGHT, fill=tk.Y)
        self.playlistbox = tk.Listbox(list_box_frame, yscrollcommand=scr.set, selectmode=tk.SINGLE, 
                                      bg="#FAFAFA", fg=FG_NORMAL, font=("Malgun Gothic", 9), 
                                      relief="flat", highlightthickness=0, selectbackground=C_PLAY)
        self.playlistbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.playlistbox.bind('<Double-1>', self.on_playlist_double_click)
        scr.config(command=self.playlistbox.yview)

    def setup_minimal_gui(self):
        # [심플 모드] 다크 배경
        self.minimal_frame = tk.Frame(self.root, bg=BG_SIMPLE)
        
        # 드래그 기능을 위해 프레임 자체에도 바인딩
        self.bind_drag_events(self.minimal_frame)

        # 오직 제목만 표시 (버튼 없음)
        self.mini_title = tk.Label(self.minimal_frame, text="No Music", font=("Malgun Gothic", 10, "bold"), 
                                   bg=BG_SIMPLE, fg=FG_SIMPLE_DEFAULT)
        # 텍스트가 가운데 오도록 pack
        self.mini_title.pack(expand=True, fill=tk.BOTH)
        
        # 라벨을 잡고도 드래그 가능하게 바인딩
        self.bind_drag_events(self.mini_title)

    def toggle_minimal_mode(self):
        if not self.is_minimal_mode:
            # -> 심플 모드 (다크) 진입
            self.normal_frame.pack_forget()
            
            # 타이틀바 제거 및 크기 축소 (버튼이 없으므로 더 얇게)
            self.root.overrideredirect(True) 
            self.root.geometry("300x40") 
            self.root.configure(bg=BG_SIMPLE) # 다크 배경
            
            self.minimal_frame.pack(fill=tk.BOTH, expand=True)
            self.is_minimal_mode = True
        else:
            # -> 일반 모드 (화이트) 복귀
            self.minimal_frame.pack_forget()
            
            self.root.overrideredirect(False)
            self.root.geometry("320x520") 
            self.root.configure(bg=BG_NORMAL) # 화이트 배경
            
            self.normal_frame.pack(fill=tk.BOTH, expand=True)
            self.is_minimal_mode = False

    def update_title_color(self):
        """색상 로직: 일반=고정, 심플=랜덤 파스텔"""
        # 1. 일반 모드는 가독성 좋은 진한 회색 고정
        self.title_label.config(fg=FG_NORMAL)
        
        # 2. 심플 모드는 랜덤 파스텔
        random_pastel = random.choice(PASTEL_COLORS)
        self.mini_title.config(fg=random_pastel)

    # --- 플레이어 로직 ---
    def play_track(self, idx):
        if not 0 <= idx < len(self.playlist): return
        self.player.stop(); self.current_index = idx; track = self.playlist[idx]
        
        # 제목 설정
        self.title_label.config(text=track['title'])
        self.mini_title.config(text=track['title'])
        
        # [중요] 색상 업데이트 호출
        self.update_title_color()
        
        self.playlistbox.selection_clear(0, tk.END); self.playlistbox.selection_set(idx); self.playlistbox.see(idx)
        def _play():
            with yt_dlp.YoutubeDL({'format':'bestaudio/best', 'quiet':True}) as ydl:
                info = ydl.extract_info(track['url'], download=False)
                media = self.instance.media_new(info['url'])
                self.player.set_media(media); self.player.play()
                self.player.audio_set_volume(self.vol_scale.get())
                self.root.after(0, lambda: self.update_play_btn("||"))
                if track['thumb']:
                    try:
                        res = requests.get(track['thumb'])
                        img = ImageTk.PhotoImage(Image.open(BytesIO(res.content)).resize((180, 135)))
                        self.root.after(0, lambda: self.thumb_label.config(image=img))
                        self.thumb_label.image = img
                    except: pass
        threading.Thread(target=_play, daemon=True).start()

    # ... (나머지 로직은 기존과 동일) ...
    def shuffle_playlist(self):
        if not self.playlist: return
        cur_url = self.playlist[self.current_index]['url'] if self.current_index != -1 else None
        random.shuffle(self.playlist)
        self.playlistbox.delete(0, tk.END)
        for s in self.playlist: self.playlistbox.insert(tk.END, s['title'])
        if cur_url:
            for i, s in enumerate(self.playlist):
                if s['url'] == cur_url:
                    self.current_index = i
                    self.playlistbox.selection_set(i)
                    break
        messagebox.showinfo("Shuffle", "Shuffled!")
    def toggle_repeat(self):
        self.repeat_mode = (self.repeat_mode + 1) % 3
        self.btn_repeat.config(text=self.repeat_icons[self.repeat_mode], bg=self.repeat_colors[self.repeat_mode])
    def play_next(self):
        if not self.playlist: return
        if self.repeat_mode == 1: self.play_track(self.current_index)
        else:
            next_idx = self.current_index + 1
            if next_idx >= len(self.playlist):
                if self.repeat_mode == 0: next_idx = 0
                else: return 
            self.play_track(next_idx)
    def update_progress_loop(self):
        if self.player.is_playing() and not self.is_dragging_time:
            cur = self.player.get_time(); tot = self.player.get_length()
            if tot > 0:
                self.time_scale.config(to=tot); self.time_scale.set(cur)
                self.lbl_cur.config(text=f"{int(cur/60000):02}:{int((cur/1000)%60):02}")
                self.lbl_tot.config(text=f"{int(tot/60000):02}:{int((tot/1000)%60):02}")
        self.root.after(500, self.update_progress_loop)
    def on_seek_drag(self, val): 
        if self.is_dragging_time: self.lbl_cur.config(text=f"{int(float(val)/60000):02}:{int((float(val)/1000)%60):02}")
    def on_slider_press(self, e): self.is_dragging_time = True
    def on_slider_release(self, e): self.player.set_time(int(self.time_scale.get())); self.is_dragging_time = False
    def start_fetch_thread(self):
        url = self.url_entry.get()
        if not url: return
        self.url_entry.delete(0, tk.END)
        self.title_label.config(text="Fetching...", fg="#999")
        threading.Thread(target=self.fetch, args=(url,), daemon=True).start()
    def fetch(self, url):
        try:
            with yt_dlp.YoutubeDL({'quiet':True, 'extract_flat':True}) as ydl:
                info = ydl.extract_info(url, download=False)
                if 'entries' in info: 
                    for e in info['entries']: self.add_song(e)
                else: self.add_song(info)
            self.root.after(0, lambda: self.title_label.config(text=f"Added {len(self.playlist)} Songs", fg=FG_NORMAL))
            if self.current_index == -1 and self.playlist: self.root.after(0, self.play_next)
        except: self.root.after(0, lambda: self.title_label.config(text="Error", fg="red"))
    def add_song(self, info):
        self.playlist.append({'title':info.get('title','?'), 'url':info.get('url', info.get('webpage_url')), 'thumb':info.get('thumbnail')})
        self.root.after(0, lambda: self.playlistbox.insert(tk.END, info.get('title','?')))
    def update_play_btn(self, text): self.btn_play.config(text=text)
    def toggle_play_pause(self):
        if self.player.is_playing(): self.player.pause(); self.update_play_btn("▶")
        else: 
            if self.current_index == -1 and self.playlist: self.play_track(0)
            else: self.player.play(); self.update_play_btn("||")
    def play_prev(self):
        if self.player.get_time() > 3000: self.player.set_time(0)
        else: self.play_track((self.current_index - 1 + len(self.playlist)) % len(self.playlist))
    def on_song_finished(self, e): self.root.after(1000, self.play_next)
    def set_volume(self, v): self.player.audio_set_volume(int(v))
    def on_playlist_double_click(self, e):
        if self.playlistbox.curselection(): self.play_track(self.playlistbox.curselection()[0])
    def start_move(self, e): self.drag_start_x = e.x; self.drag_start_y = e.y
    def stop_move(self, e): self.drag_start_x = None
    def do_move(self, e):
        if self.is_minimal_mode and self.drag_start_x:
            x = self.root.winfo_x() + e.x - self.drag_start_x
            y = self.root.winfo_y() + e.y - self.drag_start_y
            self.root.geometry(f"+{x}+{y}")

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeAudioPlayer(root)
    root.mainloop()
