import { useState } from 'react';
import './App.css';

// Fix Version: 1.2 (Force Rebuild)
console.log("App Version: 2.2 - Aggressive Compression + Cancel Button");

// Helper: Image Compression
const compressImage = async (file) => {
  return new Promise((resolve, reject) => {
    const img = new Image();
    const reader = new FileReader();

    reader.onload = (e) => {
      img.src = e.target.result;
    };

    reader.onerror = reject;

    img.onload = () => {
      const canvas = document.createElement('canvas');
      let width = img.width;
      let height = img.height;

      // Limit to 1000px (More aggressive for Mobile 4G/5G)
      const maxDim = 1000;

      if (width > height && width > maxDim) {
        height *= maxDim / width;
        width = maxDim;
      } else if (height > maxDim) {
        width *= maxDim / height;
        height = maxDim;
      }

      canvas.width = width;
      canvas.height = height;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(img, 0, 0, width, height);

      canvas.toBlob((blob) => {
        if (blob) {
          // Create new file with same name but jpeg type
          const newFile = new File([blob], file.name.replace(/\.[^/.]+$/, ".jpg"), {
            type: 'image/jpeg',
            lastModified: Date.now(),
          });
          console.log(`Compressed: ${file.size / 1024 / 1024}MB -> ${newFile.size / 1024 / 1024}MB`);
          resolve(newFile);
        } else {
          reject(new Error("Compression failed"));
        }
      }, 'image/jpeg', 0.6); // 60% Quality (High compression)
    };

    reader.readAsDataURL(file);
  });
};

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  // Form State
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [form, setForm] = useState({
    type: 'Poster',
    target: '',
    purpose: ''
  });

  // Check valid JSON helper
  const parsAnalysis = (inputData) => {
    if (typeof inputData === "string") {
      try {
        const CleanString = inputData.replace(/```json/g, '').replace(/```/g, '');
        return JSON.parse(CleanString);
      } catch (e) {
        return { raw: inputData };
      }
    }
    return inputData;
  };

  const handleFileChange = async (e) => {
    const selected = e.target.files[0];
    if (selected) {
      // Immediate Preview (Original)
      setPreview(URL.createObjectURL(selected));

      // Compress for Upload
      try {
        console.log("Compressing image...");
        const compressed = await compressImage(selected);
        setFile(compressed);
      } catch (err) {
        console.error("Compression failed, using original", err);
        setFile(selected);
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setData(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', form.type);
    formData.append('target', form.target);
    formData.append('purpose', form.purpose);

    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';

    // Timeout Promise (30 seconds)
    const timeout = new Promise((_, reject) =>
      setTimeout(() => reject(new Error("Request timed out")), 30000)
    );

    try {
      const res = await Promise.race([
        fetch(`${apiUrl}/analyze`, { method: 'POST', body: formData }),
        timeout
      ]);

      if (!res.ok) throw new Error(`Server Error: ${res.status}`);

      const json = await res.json();
      setData(parsAnalysis(json));
    } catch (err) {
      console.error(err);
      alert(`Analysis failed: ${err.message}. Please try a smaller image.`);
    } finally {
      setLoading(false);
    }
  };



  // Localization
  const isJa = navigator.language.startsWith('ja');

  const text = {
    title: isJa ? "デザイン赤ペン先生" : "Design Red Pen Mentor",
    subtitle: isJa ? "Google Gemini × デザイン理論\nあなたのデザインをAIが添削" : "Google Gemini × Design Theory\nAI corrections for your design.",
    loading: isJa ? "Googleのビッグデータと照合中..." : "Consulting Google Design Data...",
    analyzing: isJa ? "分析中: " : "Analyzing: ",
    form: {
      type: isJa ? "クリエイティブの種類" : "Creative Type",
      target: isJa ? "ターゲット (誰に？)" : "Target Audience (Who?)",
      targetPh: isJa ? "例: 20代女性、ビジネスマン" : "e.g. 20s Female, Business Professionals",
      purpose: isJa ? "目的 (何を？)" : "Purpose (Why?)",
      purposePh: isJa ? "例: 信頼獲得、クリック誘導" : "e.g. Increase clicks, Build trust",
      upload: isJa ? "ここに画像をドロップ" : "Click or Drop to Upload Image",
      submit: isJa ? "赤ペン先生に提出" : "Analyze Design",
      reset: isJa ? "次の画像を分析" : "New Analysis"
    },
    types: {
      "Poster": isJa ? "ポスター / チラシ" : "Poster / Flyer",
      "Banner": isJa ? "Webバナー" : "Web Banner",
      "App UI": isJa ? "アプリUI / Webデザイン" : "App UI / Web Design",
      "YouTube Thumbnail": isJa ? "動画: YouTubeサムネイル" : "Video: YouTube Thumbnail",
      "CM / Promotion": isJa ? "動画: CM / プロモーション" : "Video: CM / Promotion",
      "Music Video": isJa ? "動画: MV / 映像作品" : "Video: Music Video",
      "Vlog": isJa ? "動画: Vlog / 日常" : "Video: Vlog",
      "Short Video": isJa ? "動画: Tiktok / リール (縦型)" : "Video: Tiktok / Reels",
      "Photography: Portrait": isJa ? "写真: ポートレート" : "Photography: Portrait",
      "Photography: Landscape": isJa ? "写真: 風景" : "Photography: Landscape",
      "Photography: Product": isJa ? "写真: 商品 / 物撮り" : "Photography: Product",
      "Photography: Street": isJa ? "写真: ストリート / スナップ" : "Photography: Street"
    }
  };

  // --- RENDER ---

  // 1. Loading
  if (loading) {
    return (
      <div className="dashboard">
        <div className="empty-state">
          <div className="spinner">✏️</div>
          <h2>{text.loading}</h2>
          <p>{text.analyzing} {isJa ? text.types[form.type] : form.type}</p>
        </div>
      </div>
    )
  }

  // 2. Input Form (If no data yet)
  if (!data) {
    return (
      <div className="dashboard">
        <header className="hero">
          <h1 className="title">{text.title}</h1>
          <p className="version-label">v2.2</p>
          <p className="subtitle" style={{ whiteSpace: 'pre-line' }}>{text.subtitle}</p>
        </header>

        <div className="card" style={{ maxWidth: '700px', margin: '0 auto', padding: '50px' }}>
          <form onSubmit={handleSubmit} className="upload-form" style={{ display: 'flex', flexDirection: 'column', gap: '25px' }}>

            <div className="form-group">
              <label style={{ display: 'block', marginBottom: '10px', fontWeight: 'bold' }}>{text.form.type}</label>
              <select
                value={form.type}
                onChange={(e) => setForm({ ...form, type: e.target.value })}
                className="glass-input"
                style={{ padding: '15px' }}
              >
                {Object.entries(text.types).map(([key, label]) => (
                  <option key={key} value={key}>{label}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label style={{ display: 'block', marginBottom: '10px', fontWeight: 'bold' }}>{text.form.target}</label>
              <input
                type="text"
                placeholder={text.form.targetPh}
                value={form.target}
                onChange={(e) => setForm({ ...form, target: e.target.value })}
                className="glass-input"
                style={{ padding: '15px' }}
                required
              />
            </div>

            <div className="form-group">
              <label style={{ display: 'block', marginBottom: '10px', fontWeight: 'bold' }}>{text.form.purpose}</label>
              <input
                type="text"
                placeholder={text.form.purposePh}
                value={form.purpose}
                onChange={(e) => setForm({ ...form, purpose: e.target.value })}
                className="glass-input"
                style={{ padding: '15px' }}
                required
              />
            </div>

            <div className="drop-zone-visual" style={{ margin: '30px 0', padding: '50px', border: '3px dashed rgba(255,255,255,0.2)' }}>
              {preview ? (
                <div style={{ position: 'relative' }}>
                  <img src={preview} alt="Preview" style={{ maxWidth: '100%', borderRadius: '12px', boxShadow: '0 10px 30px rgba(0,0,0,0.5)' }} />
                  <button
                    type="button"
                    className="remove-image-btn"
                    onClick={() => { setFile(null); setPreview(null); }}
                    title="Remove Image"
                  >
                    ×
                  </button>
                </div>
              ) : (
                <div style={{ cursor: 'pointer', textAlign: 'center' }} onClick={() => document.getElementById('file-input').click()}>
                  <div style={{ fontSize: '3rem', marginBottom: '15px' }}>📤</div>
                  <div>{text.form.upload}</div>
                </div>
              )}
              <input
                id="file-input"
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                style={{ display: 'none' }}
              />
            </div>

            <button type="submit" className="submit-btn" disabled={!file} style={{ padding: '20px', fontSize: '1.2rem', marginTop: '10px' }}>
              {text.form.submit}
            </button>

          </form>
        </div>
      </div>
    );
  }

  // 3. Results (Tensaku Report)
  const analysis = data;
  return (
    <div className="dashboard">
      <header className="hero">
        <h1 className="title">{text.title}</h1>
        <p className="subtitle" style={{ whiteSpace: 'pre-line' }}>{text.subtitle}</p>
        <button onClick={() => { setData(null); setFile(null); setPreview(null); }} className="reset-btn">
          {text.form.reset}
        </button>
      </header>

      <div id="report-content" style={{ padding: '0px' }}>
        <div className="score-card">
          <div className="score-circle" style={{ '--score': analysis.design_score || 0 }}>
            <span className="score-value">{analysis.design_score}</span>
          </div>
          <p>Design Score</p>
        </div>

        <main className="tensaku-grid">

          {/* Left Column: Image & Good Points */}
          <div className="left-col">
            <div className="image-preview card">
              {analysis.source_image ? (
                <img src={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/uploads/${analysis.source_image}`} alt="Analysis Source" />
              ) : (
                <div style={{ padding: '20px', textAlign: 'center' }}>Image Source Not Found</div>
              )}
            </div>

            <div className="card" style={{ marginTop: '30px' }}>
              <h3 className="section-title">👍 Good Points</h3>
              {analysis.good_points && analysis.good_points.map((point, i) => (
                <div key={i} className="good-point">
                  <span>✅</span>
                  <span>{point}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Right Column: Google Data & Improvements */}
          <div className="right-col">

            {/* Google Data Insights */}
            <div className="card google-data" style={{ marginBottom: '30px' }}>
              <h3 className="section-title">📊 Google Big Data Insights</h3>

              {analysis.google_data_insights?.google_fonts_recommendation && (
                <div style={{ marginBottom: '20px' }}>
                  <span className="google-label">Google Fonts API</span>
                  <div className="google-font-rec">
                    <strong>Suggested: </strong>
                    {analysis.google_data_insights.google_fonts_recommendation.suggested_font_name}
                  </div>
                  <p style={{ fontSize: '0.9rem', opacity: 0.8 }}>
                    {analysis.google_data_insights.google_fonts_recommendation.reason}
                  </p>
                </div>
              )}

              {analysis.google_data_insights?.material_design_check && (
                <div>
                  <span className="google-label">Material Design 3</span>
                  <p><strong>Check:</strong> {analysis.google_data_insights.material_design_check.metric}</p>
                  <p style={{ color: 'var(--accent-red)', fontWeight: 'bold' }}>
                    {analysis.google_data_insights.material_design_check.verdict}:
                    <span style={{ color: 'white', fontWeight: 'normal', marginLeft: '5px' }}>
                      {analysis.google_data_insights.material_design_check.advice}
                    </span>
                  </p>
                </div>
              )}
            </div>

            {/* Improvements */}
            <div className="card">
              <h3 className="section-title">🔧 Improvement Plan</h3>
              {analysis.improvements && analysis.improvements.map((item, i) => (
                <div key={i} className="improvement-item">
                  <div className="imp-header">
                    <span className="imp-badge">{item.priority} Priority</span>
                    <span style={{ fontSize: '0.8rem', opacity: 0.7 }}>{item.naruhodo_principle}</span>
                  </div>
                  <div>{item.issue}</div>
                  <div className="imp-suggestion">
                    {item.suggestion}
                    {item.quantitative_value && (
                      <span className="imp-value">{item.quantitative_value}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>

          </div>

        </main>

        {/* Branding Watermark */}
        <div style={{ textAlign: 'center', marginTop: '50px', opacity: 0.6, fontSize: '0.9rem', borderTop: '1px solid #333', paddingTop: '20px' }}>
          Analyzed by デザイン赤ペン先生 (Design Red Pen Mentor)
        </div>
      </div>


    </div>
  );
}

export default App;
