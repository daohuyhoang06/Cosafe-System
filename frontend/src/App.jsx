import { Routes, Route } from 'react-router-dom';
import { HomePage, SearchResultPage, ProductDetailPage } from './pages';

function App() {
    return (
        <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/search" element={<SearchResultPage />} />
            <Route path="/product" element={<ProductDetailPage />} />
        </Routes>
    );
}

export default App;
