'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { FaEye, FaEyeSlash } from 'react-icons/fa';
import {
  auth,
  createUserWithEmailAndPassword,
  GoogleAuthProvider,
  signInWithPopup,
} from '../lib/firebase';  // Firebase config import

export default function RegisterPage() {
  const router = useRouter();

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
  });

  const [errors, setErrors] = useState({});
  const [passwordVisible, setPasswordVisible] = useState(false);
  const [passwordError, setPasswordError] = useState('');

  const togglePasswordVisibility = () => setPasswordVisible((prev) => !prev);

  const validatePassword = (password) => {
    const regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/;
    if (!regex.test(password)) {
      setPasswordError('Password must be at least 8 characters long, include 1 uppercase letter and 1 number.');
    } else {
      setPasswordError('');
    }
  };

  const validateForm = () => {
    const { name, email, password } = formData;
    const newErrors = {};

    const emailRegex = /^[a-zA-Z0-9._%+-]+@gmail\.com$/;
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/;

    if (!name.trim()) newErrors.name = 'Name is required';
    if (!emailRegex.test(email)) newErrors.email = 'Enter a valid Gmail address';
    if (!passwordRegex.test(password)) newErrors.password = 'Password must include uppercase and number';

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setErrors((prev) => ({ ...prev, [name]: '' }));

    if (name === 'password') validatePassword(value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (validateForm()) {
      try {
        // Firebase Email/Password Sign-Up
        await createUserWithEmailAndPassword(auth, formData.email, formData.password);
        router.push('/login');
      } catch (error) {
        const message = error.message.includes('email-already') ? 'Email already in use.' : 'Registration failed.';
        setErrors({ general: message });
        console.error('Registration error:', error.message);
      }
    }
  };

  const handleGoogleSignUp = async () => {
    try {
      const provider = new GoogleAuthProvider();
      await signInWithPopup(auth, provider);
      router.push('/login');
    } catch (error) {
      setErrors({ general: 'Google sign-in failed. Try again.' });
      console.error('Google sign-up error:', error.message);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#e9ebf0]">
      <div className="flex w-full max-w-6xl h-[90vh] bg-white rounded-xl shadow-lg overflow-hidden">
        {/* Image Section */}
        <div className="hidden md:block w-1/2">
          <img src="/cover.png" alt="Register" className="w-full h-full object-cover" />
        </div>

        {/* Form Section */}
        <div className="w-full md:w-1/2 p-10 flex flex-col justify-center">
          <div className="mb-6 flex items-center space-x-3">
            <img src="/upasthit.svg" alt="Logo" className="w-35 h-12" />
            
          </div>

          <h2 className="text-3xl font-bold text-gray-900 mb-2">Create Account<span className="text-indigo-600">.</span></h2>
          <p className="text-sm text-gray-500 mb-8">Sign up to track attendance effortlessly.</p>

          {errors.general && <div className="text-red-500 text-sm mb-3">{errors.general}</div>}

          <form className="space-y-4" onSubmit={handleSubmit}>
            {/* Name */}
            <div>
              <label htmlFor="name" className="block text-sm font-medium mb-1 text-gray-900">Full Name<span className="text-red-500">*</span></label>
              <input
                name="name"
                id="name"
                type="text"
                value={formData.name}
                onChange={handleInputChange}
                placeholder="Enter your full name"
                className={`w-full px-4 py-2 border rounded-md outline-none focus:ring-2 focus:ring-indigo-500 text-gray-900 ${errors.name ? 'border-red-500' : 'border-gray-600'}`}
              />
              {errors.name && <div className="text-red-500 text-sm mt-1">{errors.name}</div>}
            </div>

            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium mb-1 text-gray-900">Email<span className="text-red-500">*</span></label>
              <input
                name="email"
                id="email"
                type="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="Enter your email"
                className={`w-full px-4 py-2 border rounded-md outline-none focus:ring-2 focus:ring-indigo-500 text-gray-900 ${errors.email ? 'border-red-500' : 'border-gray-600'}`}
              />
              {errors.email && <div className="text-red-500 text-sm mt-1">{errors.email}</div>}
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium mb-1 text-gray-900">Password<span className="text-red-500">*</span></label>
              {passwordError && <div className="text-red-500 text-sm mb-1">{passwordError}</div>}
              <div className="relative">
                <input
                  name="password"
                  id="password"
                  type={passwordVisible ? 'text' : 'password'}
                  value={formData.password}
                  onChange={handleInputChange}
                  placeholder="Create a strong password"
                  className={`w-full px-4 py-2 border rounded-md outline-none focus:ring-2 focus:ring-indigo-500 text-gray-900 ${errors.password || passwordError ? 'border-red-500' : 'border-gray-600'}`}
                />
                {passwordVisible ? (
                  <FaEyeSlash className="absolute right-3 top-3 text-gray-400 cursor-pointer" onClick={togglePasswordVisibility} />
                ) : (
                  <FaEye className="absolute right-3 top-3 text-gray-400 cursor-pointer" onClick={togglePasswordVisibility} />
                )}
              </div>
              {errors.password && <div className="text-red-500 text-sm mt-1">{errors.password}</div>}
            </div>

            {/* Submit */}
            <button type="submit" className="w-full bg-indigo-600 text-white py-2 rounded-md hover:bg-indigo-700 transition">
              Register
            </button>

            {/* Divider */}
            <div className="text-center text-sm text-gray-400 my-2">────────  Or, Sign up with  ────────</div>

            {/* Google Sign Up */}
            <button
              type="button"
              onClick={handleGoogleSignUp}
              className="w-full border py-2 flex items-center justify-center rounded-md hover:bg-gray-100 transition"
            >
              <img src="/google.svg" alt="Google" className="w-6 h-6 mr-2" />
              <span className="text-gray-800 text-sm">Sign up with Google</span>
            </button>
          </form>

          <p className="text-sm text-gray-600 mt-6 text-center">
            Already have an account?{' '}
            <a href="/login" className="text-indigo-700 hover:underline">Log in here</a>
          </p>
        </div>
      </div>
    </div>
  );
}
