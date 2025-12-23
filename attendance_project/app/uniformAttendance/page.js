'use client'
import { useEffect, useState } from 'react';
import axios from 'axios';

const UniformAttendancePage = () => {
  const [detectionStatus, setDetectionStatus] = useState({
    shirt_detected: false,
    pants_detected: false,
    uniform_detected: false,
  });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDetectionStatus = async () => {
      try {
        setLoading(true);
        const response = await axios.get('http://localhost:5000/detection_status');
        setDetectionStatus(response.data);  // Update state with new detection status
        setError(null);
      } catch (err) {
        console.error('Error fetching detection status:', err);
        setError('Unable to connect to detection server');
      } finally {
        setLoading(false);
      }
    };

    const interval = setInterval(fetchDetectionStatus, 1000); // Poll every second
    return () => clearInterval(interval); // Clear interval on unmount
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center bg-blue-100 p-6">
      <div className="w-full max-w-6xl bg-white rounded-2xl shadow-2xl p-6 flex">
        {/* Left: Live Camera Feed */}
        <div className="w-2/3 flex justify-center items-center">
          <div className="relative w-full max-w-3xl border-4 border-gray-600 rounded-xl overflow-hidden shadow-lg">
            <img
              src="http://localhost:5000/video_feed"
              alt="Live Uniform Detection"
              className="w-full h-auto"
            />
          </div>
        </div>

        {/* Right: Detection Status */}
        <div className="w-1/3 ml-6 flex flex-col space-y-4 text-center items-center justify-center">
          {/* Shirt Status */}
          <div className="flex items-center space-x-2">
            <span className="text-xl">👕</span>
            <span className="font-medium">Shirt: </span>
            <span className={detectionStatus.shirt_detected ? 'text-green-600' : 'text-red-600'}>
              {detectionStatus.shirt_detected ? 'True' : 'False'}
            </span>
          </div>

          {/* Pants Status */}
          <div className="flex items-center space-x-2">
            <span className="text-xl">👖</span>
            <span className="font-medium">Pants: </span>
            <span className={detectionStatus.pants_detected ? 'text-green-600' : 'text-red-600'}>
              {detectionStatus.pants_detected ? 'True' : 'False'}
            </span>
          </div>

          {/* Uniform Detection */}
          <div className="mt-6 text-xl font-semibold">
            {loading ? (
              <p className="text-blue-600">⏳ Loading...</p>
            ) : error ? (
              <p className="text-red-600">⚠️ {error}</p>
            ) : detectionStatus.uniform_detected ? (
              <p className="text-green-600">✅ Uniform Detected</p>
            ) : (
              <p className="text-red-600">❌ Uniform Not Detected</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default UniformAttendancePage;


