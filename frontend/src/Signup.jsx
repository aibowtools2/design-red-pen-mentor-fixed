import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import './App.css';

import API_URL from './config';

function Signup() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSignup = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        if (password !== confirmPassword) {
            setError('パスワードが一致しません');
            setLoading(false);
            return;
        }

        try {
            const response = await fetch(`${API_URL}/auth/signup`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password }),
            });

            const data = await response.json();

            if (response.ok) {
                setSuccess(true);
                setTimeout(() => navigate('/login'), 2000);
            } else {
                setError(data.detail || '登録に失敗しました');
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
                <h2 className="title" style={{ fontSize: '2rem', marginBottom: '10px' }}>新規登録</h2>
                <p className="subtitle" style={{ marginBottom: '30px' }}>デザイン赤ペン先生へようこそ</p>

                {error && <div className="error-badge">{error}</div>}
                {success && <div className="success-badge">登録が完了しました！ログイン画面へ移動します...</div>}

                <form onSubmit={handleSignup}>
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
                            placeholder="8文字以上推奨"
                        />
                    </div>
                    <div className="input-group">
                        <label>パスワード（確認）</label>
                        <input
                            type="password"
                            className="glass-input"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            required
                            placeholder="もう一度入力してください"
                        />
                    </div>

                    <button type="submit" className="primary-btn" disabled={loading} style={{ marginTop: '20px' }}>
                        {loading ? '登録中...' : 'アカウント作成'}
                    </button>
                </form>

                <div className="auth-footer">
                    <p>すでにアカウントをお持ちですか？</p>
                    <Link to="/login" className="text-link">ログインはこちら</Link>
                </div>
            </div>
        </div>
    );
}

export default Signup;
