import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './styles/index.scss';
import Navbar from './components/Navbar/Navbar';
import Footer from './components/Footer/Footer';
import ScrollToTop from './components/ScrollToTop/ScrollToTop';
import BackToTop from './components/BackToTop/BackToTop';
import HomePage from './features/home/HomePage';

// Ağır sayfalar (recharts, lottie) ayrı parçalarda; yalnızca açılınca indirilir
const DatasetPage = lazy(() => import('./features/dataset/DatasetPage'));
const RecommendPage = lazy(() => import('./features/recommend/RecommendPage'));
const MovieDetailPage = lazy(() => import('./features/movie/MovieDetailPage'));
const CategoryDetailPage = lazy(() => import('./features/category/CategoryDetailPage'));
const NotFoundPage = lazy(() => import('./features/notfound/NotFoundPage'));

export default function App() {
  return (
    <BrowserRouter>
      <ScrollToTop />
      <Navbar />
      <Suspense fallback={<div className="page-container" style={{ minHeight: '60vh' }} />}>
        <Routes>
          <Route path="/"                  element={<HomePage />} />
          <Route path="/dataset"           element={<DatasetPage />} />
          <Route path="/recommend"         element={<RecommendPage />} />
          <Route path="/movie/:movieId"    element={<MovieDetailPage />} />
          <Route path="/category/:genre"   element={<CategoryDetailPage />} />
          <Route path="*"                  element={<NotFoundPage />} />
        </Routes>
      </Suspense>
      <Footer />
      <BackToTop />
    </BrowserRouter>
  );
}
