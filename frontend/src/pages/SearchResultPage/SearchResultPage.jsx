import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Header, Autocomplete, ImageSearchModal } from '@/components';
import { productService, emailService } from '@/services';
import './SearchResultPage.css';

const SearchResultPage = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const query = searchParams.get('q') || '';

    const [searchQuery, setSearchQuery] = useState(query);
    const [products, setProducts] = useState([]);
    const [total, setTotal] = useState(0);
    const [page, setPage] = useState(1);
    const [sortOption, setSortOption] = useState('default');
    const [isLoading, setIsLoading] = useState(false);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [email, setEmail] = useState('');

    const pageSize = 20;

    useEffect(() => {
        setSearchQuery(query);
        setPage(1);
    }, [query]);

    useEffect(() => {
        if (query) {
            searchProducts();
        }
    }, [query, page, sortOption]);

    const searchProducts = async () => {
        setIsLoading(true);
        try {
            const data = await productService.search(query, page, pageSize, sortOption);
            setProducts(data.products || []);
            setTotal(data.total || 0);
        } catch (error) {
            console.error('Search error:', error);
            setProducts([]);
        } finally {
            setIsLoading(false);
        }
    };

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

    const handleSortChange = (e) => {
        setSortOption(e.target.value);
        setPage(1);
    };

    const handleProductClick = (productName) => {
        navigate(`/product?name=${encodeURIComponent(productName)}`);
    };

    const handleEmailSubmit = async (e) => {
        e.preventDefault();
        try {
            await emailService.sendGuide(email);
            alert('Thanks! Check your email for the guide.');
            setEmail('');
        } catch (error) {
            alert('Error sending email. Please try again.');
        }
    };

    const totalPages = Math.ceil(total / pageSize);
    const maxPagesToShow = 5;
    let startPage = Math.max(1, page - Math.floor(maxPagesToShow / 2));
    let endPage = Math.min(totalPages, startPage + maxPagesToShow - 1);

    if (endPage - startPage + 1 < maxPagesToShow) {
        startPage = Math.max(1, endPage - maxPagesToShow + 1);
    }

    return (
        <div className="search-result-page">
            <Header />

            <div className="main-content">
                <form onSubmit={handleSearch} className="search-container fade-in">
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

                <div className="hazard-header fade-in delay-1">
                    <div className="hazard-links">
                        <a href="/how-we-determine-scores">HOW WE DETERMINE SCORES</a>
                        <span className="divider">|</span>
                        <a href="/learn-more-ewg-verified">LEARN MORE ABOUT EWG VERIFIED®</a>
                    </div>
                </div>

                <div className="hazard-container">
                    <img
                        src="/assets/images/hazard-score-range.png"
                        alt="Hazard Score Range"
                        className="hazard-img fade-in delay-2"
                    />
                </div>

                <div className="ewg-products">
                    <div className="fade-in delay-3">
                        <div className="header-with-sort">
                            <select
                                id="sortOption"
                                className="sort-select"
                                value={sortOption}
                                onChange={handleSortChange}
                            >
                                <option value="default">Sort: Default</option>
                                <option value="asc">Sort: A → Z</option>
                                <option value="desc">Sort: Z → A</option>
                            </select>
                            <div className="searching-title">
                                Search results for "{query}"
                            </div>
                            <p className="center-text">
                                Found {total} product{total !== 1 ? 's' : ''}
                            </p>
                        </div>
                    </div>

                    {isLoading ? (
                        <div className="loading-container">Loading...</div>
                    ) : (
                        <div className="product-grid">
                            {products.map((product, index) => (
                                <div
                                    key={index}
                                    className="product-card"
                                    onClick={() => handleProductClick(product.name)}
                                >
                                    <img
                                        src={product.link_image || '/assets/images/product-placeholder.jpg'}
                                        alt={product.name}
                                        className="product-img"
                                    />
                                    <h3 className="product-name">{product.name}</h3>
                                    <p className="product-score">Score: {product.score}</p>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {totalPages > 1 && (
                    <div className="pagination">
                        <button
                            onClick={() => setPage(Math.max(1, page - 1))}
                            disabled={page === 1}
                            className="page-btn"
                        >
                            ← Previous
                        </button>

                        {Array.from({ length: endPage - startPage + 1 }, (_, i) => startPage + i).map((p) => (
                            <button
                                key={p}
                                onClick={() => setPage(p)}
                                className={`page-btn ${p === page ? 'active' : ''}`}
                            >
                                {p}
                            </button>
                        ))}

                        <button
                            onClick={() => setPage(Math.min(totalPages, page + 1))}
                            disabled={page === totalPages}
                            className="page-btn"
                        >
                            Next →
                        </button>
                    </div>
                )}

                <div className="form-section-bg">
                    <div className="guide-title">
                        GET YOUR FREE COPY OF EWG'S QUICK TIPS FOR<br />
                        CHOOSING SAFER PERSONAL CARE PRODUCTS!
                    </div>
                    <form onSubmit={handleEmailSubmit}>
                        <div className="form-row single">
                            <div className="form-group full-width">
                                <label htmlFor="email">Email*</label>
                                <input
                                    type="email"
                                    id="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                />
                            </div>
                        </div>
                        <button type="submit" className="submit-btn">
                            SEND ME THE GUIDE
                        </button>
                    </form>
                </div>
            </div>

            <div className="background-image"></div>
        </div>
    );
};

export default SearchResultPage;
