import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import './App.css';

import API_URL from './config';

function History() {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const uid = searchParams.get('uid');
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchHistory = async () => {
            try {
                setLoading(true);
                // API_URL from config handles localhost/prod logic
                const response = await fetch(`${API_URL}/history?uid=${uid || ''}`);
                if (!response.ok) throw new Error('履歴の取得に失敗しました');
                const data = await response.json();
                setHistory(data);
            } catch (err) {
                console.error(err);
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchHistory();
    }, [uid]);

    const handleItemClick = (id) => {
        // Navigate back home with the analysis ID
        navigate(`/?id=${id}`);
    };

    return (
        <div className="history-container">
            <header className="history-header">
                <h1>分析履歴</h1>
                <p className="subtitle">過去の添削結果を確認できます</p>
            </header>

            {loading ? (
                <div className="loading-spinner">分析結果を読み込み中...</div>
            ) : error ? (
                <div className="error-message">{error}</div>
            ) : history.length === 0 ? (
                <div className="empty-state">
                    <p>まだ分析履歴がありません。</p>
                    <button onClick={() => navigate('/')} className="primary-btn">最初の添削を始める</button>
                </div>
            ) : (
                <div className="history-list">
                    {history.map((item) => (
                        <div
                            key={item.id}
                            className="history-card glass-card"
                            onClick={() => handleItemClick(item.id)}
                        >
                            <div className="card-info">
                                <span className="card-date">{new Date(item.timestamp * 1000).toLocaleDateString()}</span>
                                <span className="card-type">{item.type}</span>
                                <h3 className="card-title">{item.image}</h3>
                            </div>
                            <div className="card-score">
                                <span className="score-value">{item.score}</span>
                                <span className="score-label">点</span>
                            </div>
                            <div className="card-arrow">→</div>
                        </div>
                    ))}
                </div>
            )}

            <div className="nav-footer">
                <button onClick={() => navigate('/')} className="text-link">← ホームに戻る</button>
            </div>
        </div>
    );
}

export default History;
