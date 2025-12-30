import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import './App.css';

import API_URL from './config';

function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const response = await fetch(`${API_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password }),
            });

            const data = await response.json();

            if (response.ok) {
                localStorage.setItem('token', data.access_token);
                localStorage.setItem('user_id', data.user_id);
                localStorage.setItem('is_premium', data.is_premium);
                navigate('/app');
            } else {
                setError(data.detail || 'ログインに失敗しました');
            }
        } catch (err) {
            setError('サーバーとの通信に失敗しました');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-card glass-card">
                <h2 className="title" style={{ fontSize: '2rem', marginBottom: '10px' }}>ログイン</h2>
                <p className="subtitle" style={{ marginBottom: '30px' }}>デザイン赤ペン先生 Web版</p>

                {error && <div className="error-badge">{error}</div>}

                <form onSubmit={handleLogin}>
                    <div className="input-group">
                        <label>メールアドレス</label>
                        <input
                            type="email"
                            className="glass-input"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            placeholder="example@mail.com"
                        />
                    </div>
                    <div className="input-group">
                        <label>パスワード</label>
                        <input
                            type="password"
                            className="glass-input"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            placeholder="••••••••"
                        />
                    </div>

                    <button type="submit" className="primary-btn" disabled={loading} style={{ marginTop: '20px' }}>
                        {loading ? 'ログイン中...' : 'ログイン'}
                    </button>
                </form>

                <div className="auth-footer">
                    <p>アカウントをお持ちでないですか？</p>
                    <Link to="/signup" className="text-link">新規登録はこちら</Link>

                    <div style={{ marginTop: '20px', paddingTop: '20px', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
                        <p style={{ fontSize: '0.8rem', marginBottom: '10px', opacity: 0.7 }}>まずは添削結果のサンプルを見たい方はこちら</p>
                        <Link to="/demo" className="text-link" style={{ color: 'var(--accent-green)', fontWeight: 'bold' }}>📋 添削サンプルを見る</Link>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Login;
