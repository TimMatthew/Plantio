
import React, { useEffect, useState, useMemo, useRef } from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Link,
  useNavigate,
  useLocation,
} from 'react-router-dom';

const API_BASE = import.meta.env.VITE_API_BASE || '';

// ==================== УТИЛІТИ ====================
async function fetchJson(url, opts = {}) {
  const controller = new AbortController();
  const timeout = opts.timeout ?? 30000;
  const id = setTimeout(() => controller.abort(), timeout);
  try {
    const res = await fetch(url, { ...opts, signal: controller.signal });
    clearTimeout(id);
    if (!res.ok) {
      const txt = await res.text().catch(() => '');
      throw new Error(`HTTP ${res.status} — ${txt || res.statusText}`);
    }
    return await res.json();
  } catch (err) {
    clearTimeout(id);
    throw err;
  }
}

function useOnline() {
  const [online, setOnline] = useState(navigator.onLine);
  useEffect(() => {
    const on = () => setOnline(true);
    const off = () => setOnline(false);
    window.addEventListener('online', on);
    window.addEventListener('offline', off);
    return () => {
      window.removeEventListener('online', on);
      window.removeEventListener('offline', off);
    };
  }, []);
  return online;
}

// ==================== КОМПОНЕНТИ UI ====================
function Toast({ message, onClose }) {
  useEffect(() => {
    if (message) {
      const t = setTimeout(onClose, 4000);
      return () => clearTimeout(t);
    }
  }, [message, onClose]);
  if (!message) return null;
  return (
    <div className="fixed right-4 bottom-6 z-50 bg-black/90 text-white px-5 py-3 rounded-lg shadow-xl animate-pulse">
      {message}
    </div>
  );
}

function Progress({ value }) {
  return (
    <div className="w-full bg-gray-200 h-3 rounded-full overflow-hidden">
      <div
        className="h-full bg-gradient-to-r from-emerald-500 to-green-600 transition-all duration-300"
        style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
      />
    </div>
  );
}

function SkeletonCard() {
  return (
    <div className="animate-pulse border rounded-lg p-4 bg-white shadow">
      <div className="h-48 bg-gray-200 rounded mb-3" />
      <div className="h-5 bg-gray-200 rounded w-4/5 mb-2" />
      <div className="h-4 bg-gray-200 rounded w-1/2" />
    </div>
  );
}

// ==================== ГОЛОВНІ КОМПОНЕНТИ ====================
function Header() {
  const online = useOnline();
  const location = useLocation();

  const navItems = [
    { to: '/plants', label: 'Рослини' },
    { to: '/diseases', label: 'Хвороби' },
    { to: '/diagnose', label: 'Діагностика' },
  ];

  //const [hover, setHover] = useState(null);

  return (
    <header className="main-website-color">
      <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
        <Link to="/" className="text-2xl font-bold tracking-tight">
          <img src={"/images/logo2.png"} className="logo"/>
        </Link>


        <nav className="hidden md:flex items-center gap-2 font-ramillas">
          {navItems.map((item) => (
                <Link
                  key={item.to}
                  to={item.to}
                 className={`px-4 py-2 rounded-lg transition text-2xl ${
      location.pathname.startsWith(item.to)
        ? "font-semibold"
        : "hover:text-[#264034]"
    }`}

            >
              {item.label}
            </Link>
          ))}
        </nav>

      </div>
    </header>
  );
}

function MobileMenu({items}) {
  const [open, setOpen] = useState(false);
  return (
      <div className="md:hidden relative">
        <button
            onClick={() => setOpen((v) => !v)}
            className="px-4 py-2 bg-white/10 rounded-lg"
        >
          Меню
        </button>
        {open && (
            <div className="absolute right-0 mt-2 w-48 bg-white text-black rounded-lg shadow-xl overflow-hidden z-50">
              {items.map((item) => (
                  <Link
                      key={item.to}
                      to={item.to}
              onClick={() => setOpen(false)}
              className="block px-4 py-3 hover:bg-emerald-50 transition"
            >
              {item.label}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

function Breadcrumbs() {
  const { pathname } = useLocation();
  const parts = pathname.split('/').filter(Boolean);
  const translations = {
  plants: "Рослини",
  diseases: "Хвороби",
    diagnose: "Діагностика",
    diagnosis: "Діагностика",
  plant: "Рослина",
  about: "Про нас",
  home: "Головна",
};


  return (
    <div className="text-sm text-gray-600 mb-6">
      <Link to="/" className="hover:underline font-ramillas text-lg main-website-color">
        Головна
      </Link>
      {parts.map((p, i) => (
          <span key={i} className="capitalize font-ramillas text-lg main-website-color">
  {" / "}
            <span className="capitalize font-ramillas text-lg main-website-color">
    {
      translations[p]
          ? translations[p]
          : decodeURIComponent(p).replace(/-/g, " ")
    }
  </span>
</span>

      ))}
    </div>
  );
}

// ==================== СТОРІНКИ ====================

function Home() {
  const navigate = useNavigate();
  return (
      <div className="max-w-7xl mx-auto p-6 text-center">
      <h1 className="text-4xl font-bold mb-4 font-ramillas text-[#1F4036]">Вітаємо в Plantio</h1>
      <p className="text-lg mb-8 max-w-2xl mx-auto font-ramillas text-[#4A6F5F]">
        Діагностика хвороб рослин за фото, база знань про рослини та хвороби.
      </p>
      <div className="flex flex-wrap gap-4 justify-center">
        <button
          onClick={() => navigate('/diagnose')}
          className="px-6 py-4 bg-emerald-600 text-white rounded-lg font-semibold hover:shadow-md transition glass-card font-ramillas main-website-color"
        >
          Завантажити фото
        </button>
        <button
          onClick={() => navigate('/plants')}
          className="px-6 py-4 border-2 border-emerald-600 text-emerald-600 rounded-lg font-semibold hover:shadow-md transition glass-card font-ramillas main-website-color"
        >
          Переглянути рослини
        </button>
        <button
          onClick={() => navigate('/diseases')}
          className="px-6 py-4 border-2 border-emerald-600 text-emerald-600 rounded-lg font-semibold hover:shadow-md transition glass-card font-ramillas main-website-color"
        >
          Хвороби
        </button>
      </div>
    </div>
  );
}

function PlantsPage() {
  const [query, setQuery] = useState('');
  const [page, setPage] = useState(0);
  const size = 18;

  const [plants, setPlants] = useState([]);
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState('');

  const [selectedPlant, setSelectedPlant] = useState(null);
  const [view, setView] = useState('plants');

  useEffect(() => {
    if (view === 'plants') loadPlants();
  }, [page]);

  async function loadPlants() {
    setLoading(true);
    try {
      const q = query
        ? `?q=${encodeURIComponent(query)}&page=${page}&size=${size}`
        : `?page=${page}&size=${size}`;
      const res = await fetch(`${API_BASE}/api/v1/plants${q}`);
      const data = await res.json();
      setPlants(data.items || []);
    } catch (err) {
      setToast(err.message || 'Помилка завантаження рослин');
      setPlants([]);
    } finally {
      setLoading(false);
    }
  }

  function openPlant(p) {
    setSelectedPlant(p);
    setView('plant');
  }

  function backToList() {
    setSelectedPlant(null);
    setView('plants');
  }

function getPlantColor(name) {
  switch (name.toLowerCase()) {
    case "виноград":
      return "#546d7e";
    case "болгарський перець":
      return "#991d0b";
    case "вишня (кисла)":
      return "#541003";
    case "кукурудза":
      return "#cd8609";
    case "картопля":
      return "#647d43";
    case "гарбуз":
      return "#ff993f";
    case "полуниця":
      return "#940f0c";
    case "огірок":
      return "#21371c";
    case "малина":
      return "#fc3e2a";
    case "соняшник":
      return "#b27d2b";
    case "пшениця":
      return "#e4a33f";
    case "помідор":
      return "#a52208";
    case "соя":
      return "#4b6528";
    case "яблуня":
      return "#497303";
    default:
      return "#e0e0e0";
  }
}


 if (view === 'plant' && selectedPlant) {
  return (
    <div className="max-w-2xl mx-auto p-6">
      <Breadcrumbs />

      <h1 className="text-3xl font-bold mb-6 text-center font-ramillas text-[#1F4036]">
        {selectedPlant.plantName}
      </h1>

      <div className="bg-white rounded-2xl shadow-xl p-8 glass-card">
        <div className="text-center mb-6">
          {selectedPlant.imageUrl ? (
            <img
              src={selectedPlant.imageUrl}
              alt={selectedPlant.plantName}
              className="max-h-96 mx-auto rounded-lg shadow object-contain"
            />
          ) : (
            <div className="h-64 bg-gray-100 rounded-lg" />
          )}
        </div>

        <div className="text-center">
          <div className="text-lg font-semibold font-ramillas text-[#4A6F5F]">
            {selectedPlant.scientificName}
          </div>

          <p className="mt-4 leading-relaxed font-ramillas text-[#2E5D52]">
            {selectedPlant.description}
          </p>
        </div>

        <button
          className="mt-8 w-full py-4 bg-emerald-600 text-lg font-semibold rounded-lg font-ramillas glass-card hover:shadow-md transition text-[#E88A78]"
          onClick={backToList}
        >
          ← Повернутися до списку
        </button>
      </div>
    </div>
  );
}


  return (
    <div className="max-w-7xl mx-auto p-6">
      <Breadcrumbs />
      <h1 className="text-3xl font-bold mb-6 font-ramillas text-[#1F4036]">Рослини</h1>

      <div className="mb-6 flex gap-3">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Пошук рослин..."
          className="flex-1 p-3 custom-search  glass-card"
        />
        <button
          onClick={() => { setPage(0); loadPlants(); }}
          className="px-6 py-2 bg-emerald-600 rounded-lg glass-card hover:shadow-md transition font-bold font-ramillas text-[#3D8F97]"
        >
          Пошук
        </button>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 font-ramillas">
          {plants.map((p) => (
              <article
                  key={p._id || p.id}
                  className={`group block border rounded-lg overflow-hidden shadow hover:shadow-xl transition cursor-pointer glass-card ${getPlantColor(p.plantName)}`}
                  onClick={() => openPlant(p)}
              >
                {p.imageUrl ? (
                    <img
                        src={p.imageUrl}
                        alt={p.plantName}
                        className="h-56 w-full object-cover group-hover:scale-105 transition"
                    />
                ) : (
                    <div className="h-56 bg-gray-100 flex items-center justify-center text-gray-400">
                      Без зображення
                    </div>
                )}
                <div className="p-4">
                  <h3
                      className="font-bold text-lg"
                      style={{color: getPlantColor(p.plantName)}}
                  >
                    {p.plantName}
                  </h3>
                  <p className="text-sm text-gray-600" style={{color: getPlantColor(p.plantName)}}>{p.scientificName}</p>
                </div>
              </article>

          ))}
        </div>
      )}

      <div className="mt-8 flex justify-center gap-4">
        <button
            disabled={page === 0}
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            className="px-5 py-2 border rounded-lg disabled:opacity-50 glass-card font-ramillas main-website-color"
        >
          Назад
        </button>
        <span className="py-2 px-4 font-ramillas main-website-color">Сторінка {page + 1}</span>
        <button
            onClick={() => setPage((p) => p + 1)}
            className="px-5 py-2 border rounded-lg glass-card font-ramillas main-website-color"
        >
          Далі
        </button>
      </div>

      <Toast message={toast} onClose={() => setToast('')}/>
    </div>
  );
}


function DiseasesPage() {
  const [diseases, setDiseases] = useState([])
  const [loading, setLoading] = useState(false)
  const [q, setQ] = useState('')
  const [toast, setToast] = useState('')

  useEffect(()=>{ load() },[])
  async function load(){
    setLoading(true)
    try{
      const data = await fetchJson(`${API_BASE}/api/v1/diseases`)
      setDiseases(Array.isArray(data.items) ? data.items : data)
    }catch(err){ setToast(err.message); setDiseases([]) }
    finally{ setLoading(false) }
  }

  const filtered = useMemo(()=>{
    if(!q) return diseases
    return diseases.filter(d=> (d.diseaseName||d.name||'').toLowerCase().includes(q.toLowerCase()) || (d.plantName||'').toLowerCase().includes(q.toLowerCase()))
  },[diseases,q])

  return (
      <div className="max-w-7xl mx-auto p-6">
        <Breadcrumbs/>

        <h1 className="text-3xl font-bold mb-6 font-ramillas text-[#1F4036]">Хвороби</h1>
        <div className="mb-6 flex gap-3">
          <input value={q} onChange={e => setQ(e.target.value)} placeholder="Пошук хвороб..."
                 className="flex-1 p-3 custom-search glass-card"/>
          <button onClick={load}
                  className="px-6 py-2 bg-emerald-600 rounded-lg glass-card hover:shadow-md transition font-bold font-ramillas text-[#3D8F97]">Пошук
          </button>
        </div>

        {loading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 text-[#5F8F84]">
              {Array.from({length: 6}).map((_, i) => (<SkeletonCard key={i}/>))}
            </div>
        ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 main-website-color">
              {filtered.map((d, i) => (
                  <Link key={i} to={`/diseases/${encodeURIComponent(d._id || d.id || d.diseaseName || i)}`}
                        className="border rounded p-3 bg-white hover:shadow-md transition glass-card font-ramillas">
                    <div className="font-semibold">{d.diseaseName || d.name}</div>
                    <div className="text-sm">Рослина: {d.plantName || '—'}</div>
                    <div className="mt-2 text-sm line-clamp-3">{d.description || d.summary || ''}</div>
                  </Link>
              ))}
            </div>
        )}

        <Toast message={toast} onClose={() => setToast('')}/>
      </div>
  )
}

function DiseaseDetails() {
  const {pathname} = useLocation()
  const id = decodeURIComponent(pathname.split('/').pop())
  const [disease, setDisease] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(()=>{ load() },[id])

  async function load(){
    setLoading(true); setError('')
    try{
      const data = await fetchJson(`${API_BASE}/api/v1/diseases/${id}`)
      setDisease(data)
    }catch(err){ setError(err.message) }
    finally{ setLoading(false) }
  }

  if(loading) return <div className="p-6">Завантаження…</div>
  if(error) return <div className="p-6 text-red-600">Помилка: {error}</div>
  if(!disease) return <div className="p-6">Хвороба не знайдена</div>

  return (
  <div className="max-w-2xl mx-auto p-6">
    <Breadcrumbs />

    <h1 className="text-3xl font-bold mb-6 text-center font-ramillas text-[#1F4036]">
      {disease.diseaseName || disease.name}
    </h1>

    <div className="bg-white rounded-2xl shadow-xl p-8 glass-card">
      {}
      <div className="text-center mb-6">
        {disease.images && disease.images.length > 0 ? (
            <>
              <img
                  src={disease.images[0]}
                  alt="main"
                  className="max-h-96 mx-auto rounded-lg shadow object-contain"
              />

              {disease.images.length > 1 && (
                  <div className="grid grid-cols-3 gap-3 mt-4">
                    {disease.images.slice(0, 3).map((u, i) => (
                        <img
                            key={i}
                            src={u}
                            className="h-24 w-full object-cover rounded-lg shadow"
                        />
                    ))}
                  </div>
              )}
            </>
        ) : (
            <div className="h-64 bg-gray-100 rounded-lg"/>
        )}
      </div>

      <div className="text-center mb-6">
        <div className="text-lg font-semibold font-ramillas text-[#4A6F5F]">
          Рослина: {disease.plantName || '—'}
        </div>

        <p className="mt-4 leading-relaxed font-ramillas text-[#2E5D52]">
          {disease.description || disease.longDescription || 'Немає опису'}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-4 rounded-xl border bg-white shadow-sm glass-card">
          <h4 className="font-semibold mb-2 font-ramillas text-[#3D8F97]">Симптоми</h4>
          <div className="text-sm font-ramillas text-[#2E5D52]">
            {(disease.symptoms && disease.symptoms.join(', ')) || "З'ясовуються"}
          </div>
        </div>

        <div className="p-4 rounded-xl border bg-white shadow-sm glass-card">
          <h4 className="font-semibold mb-2 font-ramillas text-[#1A7051]">Причини</h4>
          <div className="text-sm font-ramillas text-[#2E5D52]">
            {(disease.causes && disease.causes.join(', ')) || "З'ясовуються"}
          </div>
        </div>

        <div className="p-4 rounded-xl border bg-white shadow-sm glass-card">
          <h4 className="font-semibold mb-2 font-ramillas text-[#ada7c4]">Рекомендації</h4>
          <div className="text-sm font-ramillas text-[#2E5D52]">
            {disease.treatment.join('; ') || "З'ясовуються"}
          </div>
        </div>

        <div className="p-4 rounded-xl border bg-white shadow-sm glass-card">
          <h4 className="font-semibold mb-2 font-ramillas text-[#d1a38c]">Типи лікування</h4>
          <div className="text-sm font-ramillas text-[#2E5D52]">
            {(disease.treatmentTypes && disease.treatmentTypes.join(', ')) ||
                'Органічне, Хімічне, Домашнє'}
          </div>
        </div>
      </div>

    <Link
  to="/diseases"
  className="mt-8 block w-full text-center py-4 bg-emerald-600 text-lg font-semibold rounded-lg glass-card hover:shadow-md transition text-[#E88A78]"
>
  ← Повернутися до списку
</Link>


    </div>
  </div>
  );

}

function DiagnosePage() {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [toast, setToast] = useState('');
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const [cameraOn, setCameraOn] = useState(false);

  const MAX_SIZE = 7_000_000;
  const MAX_DIM = 1600;

  useEffect(() => {
    if (file) {
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      return () => URL.revokeObjectURL(url);
    } else {
      setPreviewUrl(null);
    }
  }, [file]);

  const validateFile = (f) => {
    if (!f) return 'Файл не вибрано';
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(f.type))
      return 'Дозволені лише JPEG, PNG, WebP';
    if (f.size > MAX_SIZE) return 'Максимум 7 МБ';
    return null;
  };

  const resizeImage = async (file) => {
    const img = await createImageBitmap(file);
    if (img.width <= MAX_DIM && img.height <= MAX_DIM) return file;

    const canvas = document.createElement('canvas');
    const ratio = Math.min(MAX_DIM / img.width, MAX_DIM / img.height);
    canvas.width = img.width * ratio;
    canvas.height = img.height * ratio;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    const blob = await new Promise((res) => canvas.toBlob(res, 'image/jpeg', 0.92));
    return new File([blob], file.name.replace(/\.[^.]+$/, '') + '.jpg', { type: 'image/jpeg' });
  };

  const handleFile = (f) => {
    const err = validateFile(f);
    if (err) {
      setToast(err);
      setFile(null);
      return;
    }
    setFile(f);
    setToast('');
  };

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' },
      });
      streamRef.current = stream;
      if (videoRef.current) videoRef.current.srcObject = stream;
      setCameraOn(true);
    } catch (e) {
      setToast('Немає доступу до камери');
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
    setCameraOn(false);
  };

  const capture = () => {
    const video = videoRef.current;
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    canvas.toBlob((blob) => {
      const f = new File([blob], `photo-${Date.now()}.jpg`, { type: 'image/jpeg' });
      handleFile(f);
      stopCamera();
    }, 'image/jpeg', 0.92);
  };

  const submit = async () => {
  if (!file) return setToast('Оберіть фото');

  setUploading(true);
  setProgress(10);

  try {
    const toUpload = await resizeImage(file);

    const fileDataUrl = await new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.readAsDataURL(toUpload);
    });

    const form = new FormData();
    form.append('image', toUpload);

    const xhr = new XMLHttpRequest();
    xhr.open('POST', `${API_BASE}/api/v1/diagnose`);

    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable) {
        setProgress(Math.round((e.loaded / e.total) * 90) + 10);
      }
    };

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        const result = JSON.parse(xhr.responseText);

        const history = JSON.parse(localStorage.getItem('plantio_history') || '[]');
        history.unshift({
          at: new Date().toISOString(),
          fileName: file.name,
          fileBlob: file,
          fileDataUrl,
          result,
        });
        localStorage.setItem('plantio_history', JSON.stringify(history.slice(0, 50)));

        navigate('/diagnosis');
      } else {
        setToast('Помилка сервера: ' + xhr.status);
      }
      setUploading(false);
      setProgress(0);
    };

    xhr.onerror = () => {
      setToast('Мережева помилка');
      setUploading(false);
    };

    xhr.send(form);
  } catch (err) {
    setToast('Помилка: ' + err.message);
    setUploading(false);
  }
};


  return (
    <div className="max-w-2xl mx-auto p-6">
      <Breadcrumbs />
      <h1 className="text-3xl font-bold mb-6 text-center font-ramillas text-[#1F4036]">Діагностика за фото</h1>

      <div className="bg-white rounded-2xl shadow-xl p-8 glass-card">
        <div
          className="p-8 text-center glass-card"
          onDrop={(e) => {
            e.preventDefault();
            const f = e.dataTransfer.files[0];
            if (f) handleFile(f);
          }}
          onDragOver={(e) => e.preventDefault()}
        >
          {cameraOn ? (
            <div className="space-y-4">
              <video ref={videoRef} autoPlay playsInline className="w-full max-h-96 rounded-lg bg-black" />
              <div className="flex justify-center gap-4">
                <button onClick={capture} className="px-6 py-3 bg-emerald-600 text-white rounded-lg font-bold glass-card font-ramillas">
                  Зробити фото
                </button>
                <button onClick={stopCamera} className="px-6 py-3 border rounded-lg font-bold glass-card font-ramillas">
                  Закрити
                </button>
              </div>
            </div>
          ) : previewUrl ? (
            <img src={previewUrl} alt="preview" className="max-h-96 mx-auto rounded-lg shadow" />
          ) : (
            <p className="font-ramillas text-[#4A6F5F]">Перетягніть фото або виберіть файл</p>
          )}

          <div className="mt-6 flex justify-center gap-4 flex-wrap">
            <label className="cursor-pointer px-6 py-3 bg-emerald-100 rounded-lg font-bold glass-card hover:shadow-md transition font-ramillas text-[#E88A78]">
              Вибрати файл
              <input
                type="file"
                accept="image/*"
                className="hidden"
                onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
              />
            </label>
            <button onClick={startCamera} className="px-6 py-3 border rounded-lg font-bold font-ramillas glass-card hover:shadow-md transition text-[#E88A78]">
              Камера
            </button>
            {file && (
              <button
                onClick={() => {
                  setFile(null);
                  stopCamera();
                }}
                className="px-6 py-3 border border-red-500 rounded-lg glass-card font-bold hover:shadow-md transition font-ramillas text-[#E88A78]"
              >
                Очистити
              </button>
            )}
          </div>
        </div>

        {uploading && (
          <div className="mt-6">
            <div className="text-sm mb-2 main-website-color">Завантаження та аналіз...</div>
            <Progress value={progress} />
          </div>
        )}

        <button
          onClick={submit}
          disabled={uploading || !file}
          className="mt-8 w-full py-4 bg-emerald-600 text-lg rounded-lg disabled:opacity-50 font-bold hover:shadow-md transition font-ramillas glass-card main-website-color"
        >
          {uploading ? 'Аналіз...' : 'Запустити діагностику'}
        </button>
      </div>

      <Toast message={toast} onClose={() => setToast('')} />
    </div>
  );
}
function DiagnosisResultPage() {
  const [history] = useState(() => {
    return JSON.parse(localStorage.getItem('plantio_history') || '[]');
  });

  const [allDiseases, setAllDiseases] = useState([]);


  useEffect(() => {
  const load = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/diseases`);
      if (res.ok) {
        const data = await res.json();
        setAllDiseases(Array.isArray(data.items) ? data.items : data);
      } else {
        console.error("Не вдалося завантажити хвороби", res.status);
        setAllDiseases([]);
      }
    } catch (e) {
      console.error("Не вдалося завантажити хвороби", e);
      setAllDiseases([]);
    }
  };
  load();
}, []);

  if (history.length === 0) {
    return (
      <div className="max-w-7xl mx-auto p-6 text-center text-gray-500">
        <Breadcrumbs />
        <p>Немає результатів. Виконайте діагностику.</p>
      </div>
    );
  }

  const latest = history[0];
  const result = latest.result;
  const fileUrl = latest.fileDataUrl;

  const sorted = [...result.candidates].sort((a, b) => b.confidence - a.confidence);

  const candidatePlants = sorted.map(c => c.plant_name.toLowerCase());


  const matchingDiseases = allDiseases.filter((d) =>
  candidatePlants.includes(d.plantName?.toLowerCase())
);

  return (
    <div className="max-w-7xl mx-auto p-6">
      <Breadcrumbs />
      <h1 className="text-3xl font-bold mb-6 font-ramillas text-[#1F4036]">Результат діагностики</h1>

      <div className="bg-white rounded-xl shadow-lg p-6 mb-8 glass-card">
        <img src={fileUrl} alt="photo" className="max-h-96 mx-auto rounded-lg shadow"/>
        <p className="text-center mt-4 text-sm font-apothicaire main-website-color">
          {new Date(latest.at).toLocaleString()} — {latest.fileName}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {sorted.map((c, i) => {
          const pct = (c.confidence * 100).toFixed(1);
          const color = c.confidence > 0.6 ? 'bg-green-500' : c.confidence > 0.3 ? 'bg-yellow-500' : 'bg-red-500';
          return (
            <div
              key={i}
              className={`p-6 rounded-xl border-2 transition transform hover:scale-105 font-ramillas glass-card main-website-color ${
                i === 0 ? 'border-emerald-500 bg-emerald-50' : 'border-gray-200 bg-white'
              }`}
            >
              {i === 0 && <div className="text-sm font-bold text-emerald-700 mb-2">Найімовірніше</div>}
              <p className="font-semibold">Рослина: {c.plant_name || '—'}</p>
              <p className="font-semibold">Хвороба: {c.disease_name || 'Здорова'}</p>
              <div className="mt-3">
                <div className="flex justify-between text-sm mb-1">
                  <span>Ймовірність</span>
                  <span>{pct}%</span>
                </div>
                <div className="w-full bg-gray-200 h-4 rounded-full overflow-hidden">
                  <div className={`${color} h-full transition-all`} style={{width: `${pct}%`}}/>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-10">
        <h2 className="text-2xl font-bold mb-4 font-ramillas text-[#1F4036]">Можливі хвороби</h2>

        {matchingDiseases.length === 0 && (
          <div className="text-gray-600 glass-card">Не знайдено можливих хвороб.</div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {matchingDiseases.map((d,i) => (
            <Link
              key={i} to={`/diseases/${encodeURIComponent(d._id || d.id || d.diseaseName || i)}`}
              className="p-4 rounded-xl border bg-white shadow glass-card hover:shadow-md transition main-website-color"
            >
              <h3 className="text-lg font-bold mb-2">{d.diseaseName}</h3>
              <p className="text-sm text-gray-600 mt-2 line-clamp-3">
                {d.description}
              </p>
              <p className="text-xs text-gray-500 mt-1 italic main-website-color">Рослина: {d.plantName}</p>
            </Link>
          ))}
        </div>
      </div>

      <div className="mt-10">
        <h2 className="text-2xl font-bold mb-4 font-ramillas text-[#1F4036]">Історія</h2>
        <div className="space-y-3">
          {history.map((h, i) => (
            <div key={i}
                 className="flex justify-between items-center p-4 border rounded-lg bg-gray-50 glass-card font-ramillas main-website-color">
              <div>
                <div className="font-medium">{h.fileName}</div>
                <div className="text-sm text-gray-600 font-apothicaire main-website-color">
                  {new Date(h.at).toLocaleString()}
                </div>
              </div>
              <div className="text-sm main-website-color">
                {h.result.candidates?.length} кандидатів
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function NotFound() {
  return (
      <div className="max-w-7xl mx-auto p-6 text-center">
        <h1 className="text-3xl font-bold mb-4 font-ramillas main-website-color">404 — Сторінку не знайдено</h1>
        <Link to="/" className="text-emerald-600 underline font-ramillas main-website-color">
          На головну
        </Link>
      </div>
  );
}

export default function App() {
  return (
      <Router>
        <div className="min-h-screen bg-slate-50 app-background-home">
          <Header/>
          <main>
            <Routes>
              <Route path="/" element={<Home/>}/>
              <Route path="/plants" element={<PlantsPage/>}/>
              <Route path="/diseases" element={<DiseasesPage/>}/>
              <Route path="/diseases/:id" element={<DiseaseDetails/>}/>
              <Route path="/diagnose" element={<DiagnosePage/>}/>
              <Route path="/diagnosis" element={<DiagnosisResultPage />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}