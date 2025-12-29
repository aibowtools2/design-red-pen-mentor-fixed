
import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

const Upgrade = () => {
    const location = useLocation();
    const [success, setSuccess] = useState(false);

    useEffect(() => {
        const query = new URLSearchParams(location.search);
        if (query.get('success')) {
            setSuccess(true);
        }
    }, [location]);

    if (success) {
        return (
            <div className="dashboard" style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                <div className="card" style={{ maxWidth: '600px', width: '100%', padding: '50px', border: '1px solid #00FF00', boxShadow: '0 0 30px rgba(0, 255, 0, 0.2)', textAlign: 'center' }}>
                    <div style={{ fontSize: '4rem', marginBottom: '20px' }}>🎉</div>
                    <h2 style={{ fontSize: '2rem', marginBottom: '20px', color: '#00FF00' }}>Welcome to Premium!</h2>
                    <p style={{ fontSize: '1.2rem', lineHeight: '1.6', marginBottom: '30px' }}>
                        決済ありがとうございます。<br />
                        プレミアム機能が有効になりました。
                    </p>
                    <p style={{ fontSize: '0.9rem', opacity: 0.7, marginBottom: '30px' }}>
                        ※ 反映まで少し時間がかかる場合があります。<br />
                        LINEボットに「プラン更新」と送ってみてください。
                    </p>
                    <Link to="/" className="submit-btn" style={{ textDecoration: 'none', display: 'inline-block', padding: '15px 40px' }}>
                        Start Analyzing
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className="dashboard" style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
            <header className="hero">
                <h1 className="title" style={{ color: '#FFD700', textShadow: '0 0 20px rgba(255, 215, 0, 0.5)' }}>Premium Plan</h1>
                <p className="subtitle">Unlock Unlimited Design Analysis</p>
            </header>

            <div className="card" style={{ maxWidth: '600px', width: '100%', padding: '50px', border: '1px solid #FFD700', boxShadow: '0 0 30px rgba(255, 215, 0, 0.2)' }}>
                <h2 style={{ textAlign: 'center', fontSize: '2rem', marginBottom: '20px' }}>Unlimited Access</h2>
                <div style={{ textAlign: 'center', fontSize: '3rem', fontWeight: 'bold', color: '#FFD700', marginBottom: '30px' }}>
                    ¥350 <span style={{ fontSize: '1rem', color: '#ccc' }}>/ month</span>
                </div>

                <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 40px 0', fontSize: '1.1rem', lineHeight: '1.8' }}>
                    <li>✨ <b>Unlimited</b> AI Analysis (No daily limit)</li>
                    <li>🚀 <b>Priority</b> Processing</li>
                    <li>📂 <b>Full History</b> Access on Web</li>
                    <li>🎓 <b>Advanced</b> Design Tips</li>
                </ul>

                <div style={{ textAlign: 'center' }}>
                    {/* Placeholder for Stripe Link */}
                    <a
                        href="#"
                        onClick={(e) => { e.preventDefault(); alert("Payment link coming soon! please wait."); }}
                        className="submit-btn"
                        style={{
                            display: 'inline-block',
                            textDecoration: 'none',
                            fontSize: '1.2rem',
                            padding: '20px 50px',
                            backgroundColor: '#FFD700',
                            color: '#000',
                            fontWeight: 'bold',
                            boxShadow: '0 0 20px rgba(255, 215, 0, 0.4)'
                        }}
                    >
                        Upgrade Now
                    </a>
                </div>

                <div style={{ textAlign: 'center', marginTop: '20px' }}>
                    <p style={{ fontSize: '0.8rem', opacity: 0.7 }}>Secure payment via Stripe</p>
                </div>
            </div>

            <Link to="/" style={{ marginTop: '30px', color: '#fff', opacity: 0.7 }}>
                ← Back to Home
            </Link>
        </div>
    );
};

export default Upgrade;
