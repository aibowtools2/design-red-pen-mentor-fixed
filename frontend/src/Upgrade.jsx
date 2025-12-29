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
                    <h2 style={{ fontSize: '2rem', marginBottom: '20px', color: '#00FF00' }}>プレミアムへようこそ！</h2>
                    <p style={{ fontSize: '1.2rem', lineHeight: '1.6', marginBottom: '30px' }}>
                        決済ありがとうございます。<br />
                        プレミアム機能が有効になりました。
                    </p>
                    <p style={{ fontSize: '0.9rem', opacity: 0.7, marginBottom: '30px' }}>
                        ※ 機能が反映されるまで少し時間がかかる場合があります。<br />
                        LINEボットに「プラン更新」と送ってみてください。
                    </p>
                    <Link to="/" className="submit-btn" style={{ textDecoration: 'none', display: 'inline-block', padding: '15px 40px' }}>
                        分析を始める
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className="dashboard" style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
            <header className="hero">
                <h1 className="title" style={{ color: '#FFD700', textShadow: '0 0 20px rgba(255, 215, 0, 0.5)' }}>プレミアムプラン</h1>
                <p className="subtitle">AIデザイン添削が無制限に</p>
            </header>

            <div className="card" style={{ maxWidth: '600px', width: '100%', padding: '50px', border: '1px solid #FFD700', boxShadow: '0 0 30px rgba(255, 215, 0, 0.2)' }}>
                <h2 style={{ textAlign: 'center', fontSize: '2rem', marginBottom: '20px' }}>Unlimited Access</h2>
                <div style={{ textAlign: 'center', fontSize: '3rem', fontWeight: 'bold', color: '#FFD700', marginBottom: '30px' }}>
                    ¥350 <span style={{ fontSize: '1rem', color: '#ccc' }}>/ 月額</span>
                </div>

                <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 40px 0', fontSize: '1.1rem', lineHeight: '1.8' }}>
                    <li>✨ <b>回数無制限</b> (1日の上限なし)</li>
                    <li>🚀 <b>優先的</b> な分析処理 (混雑時も優先)</li>
                    <li>📂 <b>全履歴</b> の閲覧・保存が無期限</li>
                    <li>🎓 <b>高度な</b> デザインアドバイス機能</li>
                </ul>

                <div style={{ textAlign: 'center' }}>
                    {/* Stripe Payment Link */}
                    <a
                        href="https://buy.stripe.com/fZu14macr0CH7Kh8KKaAw02"
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
                        プレミアムに参加する
                    </a>
                </div>

                <div style={{ textAlign: 'center', marginTop: '20px' }}>
                    <p style={{ fontSize: '0.8rem', opacity: 0.7 }}>Stripeで安全に決済されます</p>
                </div>
            </div>

            {/* 注意事項セクション */}
            <div style={{ maxWidth: '600px', width: '100%', marginTop: '40px', textAlign: 'left', opacity: 0.8, fontSize: '0.85rem' }}>
                <h3 style={{ borderBottom: '1px solid #555', paddingBottom: '10px', marginBottom: '15px' }}>⚠️ 注意事項</h3>
                <ul style={{ paddingLeft: '20px', lineHeight: '1.6' }}>
                    <li>本プランは月額制のサブスクリプションです。いつでも解約可能です。</li>
                    <li>解約はStripeから届くメール、またはお問い合わせから手続き可能です。</li>
                    <li>AIの分析精度は100%を保証するものではありません。あくまでデザイン制作の補助ツールとしてご利用ください。</li>
                    <li>システムメンテナンスや障害により、一時的にサービスが利用できない場合があります。</li>
                    <li>お支払い後の返金は原則として受け付けておりません。</li>
                </ul>
            </div>

            <Link to="/" style={{ marginTop: '30px', color: '#fff', opacity: 0.7 }}>
                ← ホームに戻る
            </Link>
        </div>
    );
};

export default Upgrade;
