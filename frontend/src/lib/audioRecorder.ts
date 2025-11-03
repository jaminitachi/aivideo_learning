export class AudioRecorder {
  private mediaRecorder: MediaRecorder | null = null;
  private audioChunks: Blob[] = [];
  private stream: MediaStream | null = null;
  private mimeType: string = "audio/webm";

  // 모바일 브라우저 호환성을 위한 MIME 타입 감지
  private getSupportedMimeType(): string {
    // 지원 가능한 MIME 타입 우선순위 (모바일 호환성 고려)
    const types = [
      "audio/webm;codecs=opus", // Chrome, Firefox (데스크탑)
      "audio/webm", // Chrome (데스크탑)
      "audio/mp4", // iOS Safari, Edge
      "audio/aac", // iOS Safari
      "audio/ogg;codecs=opus", // Firefox
      "audio/wav", // 폴백
    ];

    for (const type of types) {
      if (MediaRecorder.isTypeSupported(type)) {
        return type;
      }
    }

    // 기본값 (브라우저가 자동 선택)
    return "";
  }

  async start(): Promise<void> {
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      this.mimeType = this.getSupportedMimeType();

      const options: MediaRecorderOptions = {};
      if (this.mimeType) {
        options.mimeType = this.mimeType;
      }

      this.mediaRecorder = new MediaRecorder(this.stream, options);

      this.audioChunks = [];

      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.audioChunks.push(event.data);
        }
      };

      this.mediaRecorder.start();
    } catch (error) {
      console.error("Failed to start recording:", error);
      throw error;
    }
  }

  async stop(): Promise<string> {
    return new Promise((resolve, reject) => {
      if (!this.mediaRecorder) {
        reject(new Error("No media recorder"));
        return;
      }

      this.mediaRecorder.onstop = async () => {
        // 실제 사용된 MIME 타입으로 Blob 생성 (모바일 호환성)
        const blobType = this.mimeType || "audio/webm";
        const audioBlob = new Blob(this.audioChunks, { type: blobType });
        const base64 = await this.blobToBase64(audioBlob);

        // Stop all tracks
        if (this.stream) {
          this.stream.getTracks().forEach((track) => track.stop());
        }

        resolve(base64);
      };

      this.mediaRecorder.stop();
    });
  }

  private blobToBase64(blob: Blob): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64 = reader.result as string;
        // Remove data URL prefix
        const base64Data = base64.split(",")[1];
        resolve(base64Data);
      };
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  }

  isRecording(): boolean {
    return (
      this.mediaRecorder !== null && this.mediaRecorder.state === "recording"
    );
  }
}
