import { signup, login } from "./api"
import { useState } from "react"
import "./Signup.css";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faUser, faAt, faLock, faEye, faEyeSlash, faAnchor } from '@fortawesome/free-solid-svg-icons'

function Signup({ onAuthSuccess }) {
    const [isLogin, setIsLogin] = useState(true);
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            if (isLogin) {
                const response = await login(username, password);
                localStorage.setItem('user', JSON.stringify(response));
                onAuthSuccess(response);
            } else {
                const response = await signup(username, email, password);
                localStorage.setItem('user', JSON.stringify(response));
                onAuthSuccess(response);
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="signupBlock">
            <div className="authWrapper">
                <div className="authHeader">
                    <div className="logoAuth">
                        <FontAwesomeIcon icon={faAnchor} className="anchorIconAuth"/>
                        <h1>anchor</h1>
                    </div>
                    <p className="tagline">Your AI-powered goal companion</p>
                </div>

                <div className="authContainer">
                    <div className="authTabs">
                        <button
                            className={isLogin ? 'authTab active' : 'authTab'}
                            onClick={() => setIsLogin(true)}
                            type="button"
                        >
                            Login
                        </button>
                        <button
                            className={!isLogin ? 'authTab active' : 'authTab'}
                            onClick={() => setIsLogin(false)}
                            type="button"
                        >
                            Sign Up
                        </button>
                    </div>

                    <form onSubmit={handleSubmit} className="authForm">
                        <div className="inputGroup">
                            <FontAwesomeIcon icon={faUser} className="inputIcon" />
                            <input
                                type="text"
                                placeholder="Username"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                required
                                className="authInput"
                            />
                        </div>

                        {!isLogin && (
                            <div className="inputGroup">
                                <FontAwesomeIcon icon={faAt} className="inputIcon" />
                                <input
                                    type="email"
                                    placeholder="Email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                    className="authInput"
                                />
                            </div>
                        )}

                        <div className="inputGroup">
                            <FontAwesomeIcon icon={faLock} className="inputIcon" />
                            <input
                                type={showPassword ? "text" : "password"}
                                placeholder="Password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                className="authInput"
                            />
                            <FontAwesomeIcon
                                icon={showPassword ? faEyeSlash : faEye}
                                className="eyeIcon"
                                onClick={() => setShowPassword(!showPassword)}
                            />
                        </div>

                        {error && <p className="error">{error}</p>}

                        <button type="submit" disabled={loading} className="authButton">
                            {loading ? 'Please wait...' : (isLogin ? 'Login' : 'Sign Up')}
                        </button>
                    </form>
                </div>
            </div>
        </div>
    )
}

export default Signup;