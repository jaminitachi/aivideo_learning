"use client";

import { useEffect, useState } from "react";
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

  const [avatarSession, setAvatarSession] = useState<AvatarSession | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>();

  // Create session on mount
  useEffect(() => {
    createAvatarSession();
  }, []);

  // Cleanup: Delete Tavus session when component unmounts
  useEffect(() => {
    return () => {
      if (avatarSession) {
        deleteTavusSession(avatarSession.session_id);
      }
    };
  }, [avatarSession]);

  // Handle browser close/refresh
  useEffect(() => {
    const handleBeforeUnload = () => {
      if (avatarSession) {
        // Use sendBeacon for reliable cleanup on page unload
        navigator.sendBeacon(
          `${process.env.NEXT_PUBLIC_API_URL}/api/avatar-sessions/tavus/${avatarSession.session_id}`,
          JSON.stringify({})
        );
      }
    };

    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => window.removeEventListener("beforeunload", handleBeforeUnload);
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

  const endSession = async () => {
    // Delete session before leaving
    if (avatarSession) {
      await deleteTavusSession(avatarSession.session_id);
    }
    router.push("/");
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-900 to-indigo-900 border-b border-purple-700 px-6 py-4 shadow-lg">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-white">English Correction Teacher</h1>
            <p className="text-sm text-purple-200 mt-1">
              🎯 Real-time correction • Voice-only practice
            </p>
          </div>

          <button
            onClick={endSession}
            className="flex items-center space-x-2 px-6 py-3 bg-red-600 hover:bg-red-700 rounded-lg transition-colors shadow-md font-semibold"
          >
            <Home size={20} />
            <span>End Session</span>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {loading && (
          <div className="flex flex-col items-center justify-center h-96">
            <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-purple-500 mb-4"></div>
            <p className="text-gray-400">Connecting to your English teacher...</p>
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
          <div className="space-y-6">
            {/* Video Container */}
            <div className="bg-gray-800 rounded-2xl overflow-hidden shadow-2xl">
              <div className="aspect-video relative">
                <iframe
                  src={avatarSession.room_url}
                  allow="camera; microphone; fullscreen; display-capture; autoplay"
                  className="w-full h-full"
                  style={{ border: "none" }}
                />
              </div>
            </div>

            {/* Status Banner */}
            <div className="bg-gradient-to-r from-green-800/30 to-emerald-800/30 border border-green-500/50 rounded-lg p-6">
              <div className="flex items-center justify-center space-x-4">
                <div className="w-4 h-4 bg-green-500 rounded-full animate-pulse shadow-lg shadow-green-500/50"></div>
                <span className="text-green-300 text-lg font-semibold">
                  🎙️ Session Active - Speak freely!
                </span>
              </div>
            </div>

            {/* Instructions */}
            <div className="bg-purple-900/20 border border-purple-500/30 rounded-lg p-8">
              <h3 className="text-2xl font-bold mb-4 text-purple-200">📚 How This Works:</h3>
              <div className="grid md:grid-cols-2 gap-6 text-gray-300">
                <div className="space-y-3">
                  <div className="flex items-start">
                    <span className="font-bold text-purple-400 mr-3 text-xl">✓</span>
                    <div>
                      <p className="font-semibold text-white">Voice-Only Practice</p>
                      <p className="text-sm">Your camera is off - just speak naturally!</p>
                    </div>
                  </div>
                  <div className="flex items-start">
                    <span className="font-bold text-purple-400 mr-3 text-xl">✓</span>
                    <div>
                      <p className="font-semibold text-white">Immediate Corrections</p>
                      <p className="text-sm">Every mistake is a learning opportunity</p>
                    </div>
                  </div>
                </div>
                <div className="space-y-3">
                  <div className="flex items-start">
                    <span className="font-bold text-purple-400 mr-3 text-xl">✓</span>
                    <div>
                      <p className="font-semibold text-white">Practice & Repeat</p>
                      <p className="text-sm">You'll be asked to say it correctly</p>
                    </div>
                  </div>
                  <div className="flex items-start">
                    <span className="font-bold text-purple-400 mr-3 text-xl">✓</span>
                    <div>
                      <p className="font-semibold text-white">Natural Conversations</p>
                      <p className="text-sm">Talk about topics that interest you</p>
                    </div>
                  </div>
                </div>
              </div>
              <div className="mt-6 p-4 bg-yellow-900/30 border border-yellow-500/50 rounded-lg">
                <p className="text-yellow-200 text-sm">
                  <span className="font-bold">💡 Tip:</span> Don't be afraid to make mistakes!
                  The teacher will gently correct you and help you improve.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
