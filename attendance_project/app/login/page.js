'use client';

import { FaGoogle, FaEye, FaEyeSlash } from 'react-icons/fa';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { auth, signInWithEmailAndPassword, signInWithPopup, googleProvider } from '../lib/firebase';  // Adjust the import to match your file structure

export default function LoginPage() {
  const router = useRouter();
  const [passwordVisible, setPasswordVisible] = useState(false);
  const [password, setPassword] = useState("");
  const [passwordError, setPasswordError] = useState("");
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const togglePasswordVisibility = () => {
    setPasswordVisible(!passwordVisible);
  };

  const validatePassword = (password) => {
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/;
    if (password && !passwordRegex.test(password)) {
      setPasswordError("Password must be at least 8 characters, with 1 uppercase and 1 number.");
    } else {
      setPasswordError("");
    }
  };

  const handlePasswordChange = (e) => {
    const newPassword = e.target.value;
    setPassword(newPassword);
    validatePassword(newPassword);
  };

  const handleEmailChange = (e) => {
    setEmail(e.target.value);
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await signInWithEmailAndPassword(auth, email, password);  // Using the imported function from Firebase config
      setLoading(false);
      router.push('/dashboard');  // Redirect on success
      alert("Login Successful!");
    } catch (err) {
      setLoading(false);
      setError("Invalid email or password.");
    }
  };

  const handleGoogleSignIn = async () => {
    try {
      await signInWithPopup(auth, googleProvider);  // Using the imported provider for Google sign-in
      router.push('/dashboard');  // Redirect on success
      alert("Login Successful!");
    } catch (err) {
      console.log(err.message);
      alert("Login failed.");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#e9ebf0]">
      <div className="flex w-full max-w-6xl h-[90vh] bg-white rounded-xl shadow-lg overflow-hidden">
        {/* Left: Form Section */}
        <div className="w-full md:w-1/2 p-10 flex flex-col justify-center">
          {/* Logo */}
          <div className="mb-6 flex items-center space-x-3">
            <img src="/upasthit.svg" alt="Logo" className="w-35 h-12" />
            
          </div>

          {/* Heading */}
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome back<span className="text-indigo-600"> !</span>
          </h2>
          <p className="text-sm text-gray-500 mb-8">
            Enter to get unlimited access to data & information.
          </p>

          {/* Login Form */}
          <form className="space-y-4" onSubmit={handleLogin}>
            {/* Email */}
            <div>
              <label className="block text-sm font-medium mb-1 text-gray-900">
                Email<span className="text-red-500"> *</span>
              </label>
              <input
                type="email"
                placeholder="Enter your mail address"
                className="w-full px-4 py-2 border border-gray-600 rounded-md outline-none focus:ring-2 focus:ring-indigo-500 text-gray-900"
                value={email}
                onChange={handleEmailChange}
              />
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium mb-1 text-gray-900">
                Password<span className="text-red-500"> *</span>
              </label>
              {passwordError && <div className="text-red-500 text-sm mb-2">{passwordError}</div>}
              <div className="relative">
                <input
                  type={passwordVisible ? 'text' : 'password'}
                  placeholder="Enter password"
                  value={password}
                  onChange={handlePasswordChange}
                  className={`w-full px-4 py-2 border rounded-md outline-none focus:ring-2 focus:ring-indigo-500 text-gray-900 ${passwordError ? 'border-red-500' : 'border-gray-600'}`}
                />
                {passwordVisible ? (
                  <FaEyeSlash
                    className="absolute right-3 top-3 text-gray-400 cursor-pointer"
                    onClick={togglePasswordVisibility}
                  />
                ) : (
                  <FaEye
                    className="absolute right-3 top-3 text-gray-400 cursor-pointer"
                    onClick={togglePasswordVisibility}
                  />
                )}
              </div>
            </div>

            {/* Remember & Forgot */}
            <div className="flex items-center justify-between text-sm">
              <label className="flex items-center text-gray-900">
                <input type="checkbox" className="mr-2 accent-indigo-600" />
                Remember me
              </label>
              <a href="#" className="text-indigo-700 hover:underline text-2xlbold">
                Forgot your password ?
              </a>
            </div>

            {/* Login Button */}
            <button
              type="submit"
              className="w-full bg-indigo-600 text-white py-2 rounded-md hover:bg-indigo-700 transition"
              disabled={loading}
            >
              {loading ? 'Logging In...' : 'Log In'}
            </button>

            {/* Divider */}
            <div className="text-center text-sm text-gray-400">────────  Or, Login with  ────────</div>

            {/* Google Sign-In */}
            <button
              type="button"
              className="w-full border py-2 flex items-center justify-center rounded-md hover:bg-gray-100 transition"
              onClick={handleGoogleSignIn}
            >
              <img src="/google.svg" alt="Google" className="w-6 h-6 mr-2" />
              <span className="text-gray-800 text-sm">Sign in with Google</span>
            </button>
          </form>

          {/* Register link */}
          <p className="text-sm text-gray-600 mt-6 text-center">
            Don’t have an account ?{' '}
            <a
              href="#"
              onClick={() => router.push('/register')}
              className="text-indigo-700 hover:underline"
            >
              Register here
            </a>
          </p>
        </div>

        {/* Right: Image Section */}
        <div className="hidden md:block w-1/2">
          <img
            src="/cover.png"
            alt="Login Illustration"
            className="w-full h-full object-cover"
          />
        </div>
      </div>
    </div>
  );
}
