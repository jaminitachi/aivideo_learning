"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import { Home } from "lucide-react";

interface AvatarSession {
  session_id: string;
  room_url: string;
  provider: string;
}

export default function SimpleLearningPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.sessionId as string;

  const [avatarSession, setAvatarSession] = useState<AvatarSession | null>(
    null
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();
  const [timeRemaining, setTimeRemaining] = useState<number>(120); // 1분 타이머 (초 단위)
  const [sessionStartTime, setSessionStartTime] = useState<number | null>(null);

  // Create session on mount
  useEffect(() => {
    createAvatarSession();
  }, []);

  // 1분 타이머 관리 및 자동 세션 종료
  useEffect(() => {
    if (!avatarSession || !sessionStartTime) return;

    const interval = setInterval(async () => {
      const elapsed = Math.floor((Date.now() - sessionStartTime) / 1000);
      const remaining = Math.max(0, 120 - elapsed);
      setTimeRemaining(remaining);

      // 1분 경과 시 자동 종료
      if (remaining === 0) {
        clearInterval(interval);
        // 자동으로 세션 종료
        if (avatarSession) {
          await deleteTavusSession(avatarSession.session_id);
        }
        setSessionStartTime(null);
        router.push("/");
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [avatarSession, sessionStartTime, router]);

  // Cleanup: Delete Tavus session when component unmounts
  useEffect(() => {
    return () => {
      if (avatarSession) {
        // Synchronous cleanup on unmount
        deleteTavusSession(avatarSession.session_id);
      }
    };
  }, [avatarSession]);

  // Handle browser close/refresh - DELETE 요청 보장
  useEffect(() => {
    const handlePageUnload = () => {
      if (avatarSession) {
        // fetch with keepalive는 DELETE 메서드를 지원하므로 이를 사용
        // pagehide 이벤트도 함께 처리하여 더 확실하게 종료
        fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/avatar-sessions/tavus/${avatarSession.session_id}`,
          {
            method: "DELETE",
            keepalive: true, // 페이지가 언로드되어도 요청 완료 보장
          }
        ).catch((err) => {
          console.error("Failed to delete session on unload:", err);
        });
      }
    };

    // beforeunload와 pagehide 모두 처리
    window.addEventListener("beforeunload", handlePageUnload);
    window.addEventListener("pagehide", handlePageUnload);

    return () => {
      window.removeEventListener("beforeunload", handlePageUnload);
      window.removeEventListener("pagehide", handlePageUnload);
    };
  }, [avatarSession]);

  const createAvatarSession = async () => {
    // Delete previous session before creating new one
    if (avatarSession) {
      await deleteTavusSession(avatarSession.session_id);
    }

    setLoading(true);
    setError(undefined);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/avatar-sessions/create`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({}),
        }
      );

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || response.statusText);
      }

      const data: AvatarSession = await response.json();
      setAvatarSession(data);
      setSessionStartTime(Date.now()); // 세션 시작 시간 기록
      setTimeRemaining(120); // 타이머 초기화
    } catch (err) {
      console.error("Error creating avatar session:", err);
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const deleteTavusSession = async (conversationId: string) => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/avatar-sessions/tavus/${conversationId}`,
        { method: "DELETE" }
      );

      if (response.ok) {
        console.log(`Tavus session ${conversationId} deleted successfully`);
      }
    } catch (err) {
      console.error("Error deleting Tavus session:", err);
    }
  };

  const endSession = useCallback(async () => {
    // Delete session before leaving
    if (avatarSession) {
      await deleteTavusSession(avatarSession.session_id);
    }
    setSessionStartTime(null); // 타이머 리셋
    router.push("/");
  }, [avatarSession, router]);

  // 시간을 MM:SS 형식으로 포맷팅
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-900 to-indigo-900 border-b border-purple-700 px-4 sm:px-6 py-3 sm:py-4 shadow-lg">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
          <div className="flex-1">
            <h1 className="text-xl sm:text-3xl font-bold text-white">
              English Correction Teacher
            </h1>
            <p className="text-xs sm:text-sm text-purple-200 mt-1">
              🎯 Real-time correction • Voice-only practice
            </p>
          </div>

          <div className="flex items-center gap-3 w-full sm:w-auto">
            {/* 1분 타이머 표시 */}
            {avatarSession && sessionStartTime !== null && (
              <div className="flex items-center gap-2 px-4 py-2 bg-yellow-600/20 border border-yellow-500/50 rounded-lg">
                <span className="text-yellow-300 text-sm sm:text-base font-mono font-semibold">
                  ⏱️ {formatTime(timeRemaining)}
                </span>
              </div>
            )}

            <button
              onClick={endSession}
              className="flex items-center space-x-2 px-4 sm:px-6 py-2 sm:py-3 bg-red-600 hover:bg-red-700 rounded-lg transition-colors shadow-md font-semibold text-sm sm:text-base flex-1 sm:flex-initial justify-center"
            >
              <Home size={18} />
              <span>End Session</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Content - 모바일 반응형 패딩 */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4 sm:py-8">
        {loading && (
          <div className="flex flex-col items-center justify-center h-96">
            <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-purple-500 mb-4"></div>
            <p className="text-gray-400">
              Connecting to your English teacher...
            </p>
          </div>
        )}

        {error && (
          <div className="bg-red-900/20 border border-red-500 rounded-lg p-6 text-center">
            <p className="text-red-400 text-lg font-semibold mb-2">Error</p>
            <p className="text-red-300">{error}</p>
            <button
              onClick={createAvatarSession}
              className="mt-4 px-6 py-2 bg-red-600 hover:bg-red-700 rounded-lg transition-colors"
            >
              Retry
            </button>
          </div>
        )}

        {avatarSession && !loading && (
          <div className="space-y-4 sm:space-y-6">
            {/* Video Container - 모바일 최적화 */}
            <div className="bg-gray-800 rounded-xl sm:rounded-2xl overflow-hidden shadow-2xl">
              <div className="aspect-video relative w-full">
                <iframe
                  src={avatarSession.room_url}
                  allow="microphone; fullscreen; display-capture; autoplay;"
                  allowFullScreen
                  className="w-full h-full touch-pan-y touch-pinch-zoom"
                  style={{ border: "none", touchAction: "manipulation" }}
                  loading="eager"
                  title="Tavus Video Session"
                />
              </div>
            </div>

            {/* Status Banner */}
            <div className="bg-gradient-to-r from-green-800/30 to-emerald-800/30 border border-green-500/50 rounded-lg p-4 sm:p-6">
              <div className="flex flex-col sm:flex-row items-center justify-center gap-2 sm:gap-4">
                <div className="w-3 h-3 sm:w-4 sm:h-4 bg-green-500 rounded-full animate-pulse shadow-lg shadow-green-500/50"></div>
                <span className="text-green-300 text-sm sm:text-lg font-semibold text-center">
                  🎙️ Session Active - Speak freely!
                </span>
                {timeRemaining <= 10 && timeRemaining > 0 && (
                  <span className="text-yellow-300 text-sm sm:text-base font-semibold animate-pulse">
                    ⚠️ {timeRemaining}초 남았습니다
                  </span>
                )}
              </div>
            </div>

            {/* Instructions */}
            <div className="bg-purple-900/20 border border-purple-500/30 rounded-lg p-4 sm:p-6 md:p-8">
              <h3 className="text-xl sm:text-2xl font-bold mb-3 sm:mb-4 text-purple-200">
                📚 How This Works:
              </h3>
              <div className="grid md:grid-cols-2 gap-4 sm:gap-6 text-gray-300">
                <div className="space-y-3">
                  <div className="flex items-start">
                    <span className="font-bold text-purple-400 mr-3 text-xl">
                      ✓
                    </span>
                    <div>
                      <p className="font-semibold text-white">
                        Voice-Only Practice
                      </p>
                      <p className="text-sm">
                        Your camera is off - just speak naturally!
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start">
                    <span className="font-bold text-purple-400 mr-3 text-xl">
                      ✓
                    </span>
                    <div>
                      <p className="font-semibold text-white">
                        Immediate Corrections
                      </p>
                      <p className="text-sm">
                        Every mistake is a learning opportunity
                      </p>
                    </div>
                  </div>
                </div>
                <div className="space-y-3">
                  <div className="flex items-start">
                    <span className="font-bold text-purple-400 mr-3 text-xl">
                      ✓
                    </span>
                    <div>
                      <p className="font-semibold text-white">
                        Practice & Repeat
                      </p>
                      <p className="text-sm">
                        You'll be asked to say it correctly
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start">
                    <span className="font-bold text-purple-400 mr-3 text-xl">
                      ✓
                    </span>
                    <div>
                      <p className="font-semibold text-white">
                        Natural Conversations
                      </p>
                      <p className="text-sm">
                        Talk about topics that interest you
                      </p>
                    </div>
                  </div>
                </div>
              </div>
              <div className="mt-4 sm:mt-6 p-3 sm:p-4 bg-yellow-900/30 border border-yellow-500/50 rounded-lg">
                <p className="text-yellow-200 text-xs sm:text-sm">
                  <span className="font-bold">💡 Tip:</span> Don't be afraid to
                  make mistakes! The teacher will gently correct you and help
                  you improve.
                </p>
                <p className="text-yellow-200 text-xs sm:text-sm mt-2">
                  <span className="font-bold">⏰ Note:</span> This session will
                  automatically end after 2 minute.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
