import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import './App.css';

import API_URL, { STRIPE_PAYMENT_LINK } from './config';

function Signup() {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [isPremium, setIsPremium] = useState(true); // Default to Premium
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

        // Username validation
        if (!/^[a-z0-9]{1,10}$/.test(username)) {
            setError('ユーザー名は半角英数字（小文字）・10文字以内で入力してください');
            setLoading(false);
            return;
        }

        try {
            const response = await fetch(`${API_URL}/auth/signup`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password }),
            });

            const data = await response.json();

            if (response.ok) {
                setSuccess(true);

                if (isPremium && data.user_id) {
                    // Redirect to Stripe
                    setTimeout(() => {
                        window.location.href = `${STRIPE_PAYMENT_LINK}?client_reference_id=${data.user_id}`;
                    }, 1500);
                } else {
                    // Normal redirect
                    setTimeout(() => navigate('/login'), 2000);
                }
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
                {success && (
                    <div className="success-badge">
                        {isPremium ? 'アカウント作成＆確認メール送信！決済へ移動します...' : '登録完了！確認メールを送信しました。'}
                    </div>
                )}

                <form onSubmit={handleSignup}>
                    <div className="input-group">
                        <label>ユーザー名 <span style={{ fontSize: '0.8em', opacity: 0.7 }}>(英数小文字 10文字以内)</span></label>
                        <input
                            type="text"
                            className="glass-input"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                            placeholder="user123"
                            pattern="[a-z0-9]{1,10}"
                            title="半角英数字（小文字）、10文字以内"
                        />
                    </div>
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

                    <div className="plan-selection" style={{ marginTop: '20px', padding: '15px', background: 'rgba(255,255,255,0.05)', borderRadius: '12px' }}>
                        <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer', gap: '10px' }}>
                            <input
                                type="checkbox"
                                checked={isPremium}
                                onChange={(e) => setIsPremium(e.target.checked)}
                                style={{ transform: 'scale(1.2)' }}
                            />
                            <div style={{ textAlign: 'left' }}>
                                <div style={{ fontWeight: 'bold', fontSize: '1rem', color: isPremium ? '#00f2fe' : 'inherit' }}>
                                    Standard Plan (月額 ¥500)
                                </div>
                                <div style={{ fontSize: '0.8rem', color: '#aaa' }}>
                                    無制限AI分析・詳細レポート
                                </div>
                            </div>
                        </label>
                    </div>

                    <button type="submit" className="primary-btn" disabled={loading} style={{ marginTop: '20px', width: '100%' }}>
                        {loading ? '処理中...' : (isPremium ? '登録して決済へ進む' : 'アカウント作成')}
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
