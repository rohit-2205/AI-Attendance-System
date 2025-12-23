import { initializeApp } from "firebase/app";
import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword, GoogleAuthProvider, signInWithPopup,signOut, updatePassword } from "firebase/auth";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  authDomain: "upasthit-88cc3.firebaseapp.com",
  projectId: "upasthit-88cc3",
  storageBucket: "upasthit-88cc3.firebasestorage.app",
  messagingSenderId: "940694722362",
  appId: "1:940694722362:web:f0014894532edc71cd6203",
  measurementId: "G-DNZCHZ65TJ",
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase Authentication
const auth = getAuth(app);

// Google Authentication Provider
const googleProvider = new GoogleAuthProvider();

// Export Firebase services
export { auth, createUserWithEmailAndPassword, signInWithEmailAndPassword, googleProvider, signInWithPopup , signOut, updatePassword};


// // Import the functions you need from the SDKs you need
// import { initializeApp } from "firebase/app";
// import { getAnalytics } from "firebase/analytics";
// // TODO: Add SDKs for Firebase products that you want to use
// // https://firebase.google.com/docs/web/setup#available-libraries

// // Your web app's Firebase configuration
// // For Firebase JS SDK v7.20.0 and later, measurementId is optional
// const firebaseConfig = {
//   apiKey: "AIzaSyAM85UH98yD322Zl5S4mPFa321oKRFYF4Y",
//   authDomain: "upasthit-88cc3.firebaseapp.com",
//   projectId: "upasthit-88cc3",
//   storageBucket: "upasthit-88cc3.firebasestorage.app",
//   messagingSenderId: "940694722362",
//   appId: "1:940694722362:web:f0014894532edc71cd6203",
//   measurementId: "G-DNZCHZ65TJ"
// };

// // Initialize Firebase
// const app = initializeApp(firebaseConfig);

// const analytics = getAnalytics(app);
