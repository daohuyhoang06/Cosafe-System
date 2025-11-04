import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Header, Autocomplete, ImageSearchModal } from '@/components';
import './HomePage.css';

const HomePage = () => {
    const [searchQuery, setSearchQuery] = useState('');
    const [isModalOpen, setIsModalOpen] = useState(false);
    const navigate = useNavigate();

    const handleSearch = (e) => {
        e.preventDefault();
        if (searchQuery.trim()) {
            navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
        }
    };

    const handleAutocompleteSelect = (product) => {
        setSearchQuery(product.name);
        navigate(`/search?q=${encodeURIComponent(product.name)}`);
    };

    const handleImageSearch = (productName) => {
        setSearchQuery(productName);
        navigate(`/search?q=${encodeURIComponent(productName)}`);
    };

    return (
        <div className="home-page">
            <Header />

            <main className="main-content">
                <h1 className="fade-in">
                    Your guide to safer<br />personal care products
                </h1>
                <p className="fade-in delay-1">
                    Backed by science. Designed for you. Learn what's really in your
                    personal care products.
                </p>

                <form onSubmit={handleSearch} className="search-container fade-in delay-2">
                    <Autocomplete
                        value={searchQuery}
                        onChange={setSearchQuery}
                        onSelect={handleAutocompleteSelect}
                        placeholder="Search for a product"
                    />
                    <button
                        type="button"
                        className="image-search-btn"
                        onClick={() => setIsModalOpen(true)}
                        title="Search by image"
                    >
                        <img src="/assets/images/camera-icon.png" alt="Search by image" />
                    </button>
                </form>

                <ImageSearchModal
                    isOpen={isModalOpen}
                    onClose={() => setIsModalOpen(false)}
                    onSearch={handleImageSearch}
                />

                <div className="stats fade-in delay-3">
                    <div>
                        <strong>127,485</strong><br />Products
                    </div>
                    <div>
                        <strong>6,101</strong><br />Brands
                    </div>
                    <div>
                        <strong>2,522</strong><br />EWG Verified<sup>®</sup><br />Products
                    </div>
                </div>
            </main>

            <div className="background-image"></div>

            <div className="notification fade-in delay-4">
                We've updated the science and safety of several ingredients and the
                products that use them in Skin Deep<sup>®</sup>. Thanks again for choosing
                healthier products for you and your family!
            </div>
        </div>
    );
};

export default HomePage;
