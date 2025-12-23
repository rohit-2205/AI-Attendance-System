'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { auth } from './lib/firebase';
import { onAuthStateChanged } from 'firebase/auth';
import { ArrowRight, LogIn } from 'lucide-react';

export default function Home() {
  const router = useRouter();
  const [user, setUser] = useState(null);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
    });

    return () => unsubscribe();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-tr from-violet-500 to-indigo-700 text-white flex items-center justify-center px-6">
      <div className="text-center max-w-3xl animate-fade-in-up">
        <h1 className="text-5xl font-extrabold mb-4 drop-shadow-md">Smart Attendance System</h1>
        <p className="text-xl text-gray-200 mb-10">Empowering institutions with Real-Time and Automated face and uniform detection attendance tracking.</p>

        <div className="flex flex-col md:flex-row items-center justify-center gap-4">
          {!user ? (
            <>
              <button
                onClick={() => router.push('/login')}
                className="bg-white text-violet-700 px-6 py-3 rounded-xl font-semibold flex items-center gap-2 hover:bg-violet-100 transition"
              >
                <LogIn size={18} />
                Teacher Login
              </button>
              <button
                onClick={() => router.push('/uniformAttendance')}
                className="bg-green-400 text-white px-6 py-3 rounded-xl font-semibold flex items-center gap-2 hover:bg-green-500 transition"
              >
                <ArrowRight size={18} />
                Mark Attendance
              </button>
            </>
          ) : (
            <button
              onClick={() => router.push('/dashboard')}
              className="bg-white text-violet-700 px-6 py-3 rounded-xl font-semibold flex items-center gap-2 hover:bg-violet-100 transition"
            >
              <ArrowRight size={18} />
              Go to Dashboard
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
