/* ================================================
   VirtualFit Pro — Data v3.0
   Categories: Men | Women | Boys | Girls | Mid-Age
   Total: 50 Products | Real Unsplash Images
   All Virtual Try-On Compatible ✅
   ================================================ */

const API = '/api';

const PRODUCTS = [

  // ═══════════════════════════════════════════
  //  MEN — 12 Products (Age 18-35)
  // ═══════════════════════════════════════════

  {id:1,  gender:'men', name:'Classic White Oxford Shirt',    brand:'Elegance',  cat:'shirts',  price:2800, old:3500,  img:'https://images.unsplash.com/photo-1602810316693-3667c854239a?w=600&q=80', rating:4.8, rev:124, badge:'new',  sizes:['XS','S','M','L','XL','XXL'], desc:'Premium 100% cotton Oxford shirt with tailored fit. Perfect for office or smart-casual occasions. Wrinkle-resistant fabric.'},

  {id:2,  gender:'men', name:'Navy Blue Slim Blazer',          brand:'FormFit',   cat:'jackets', price:8500, old:12000, img:'https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=600&q=80', rating:4.9, rev:87,  badge:'sale', sizes:['S','M','L','XL','XXL'],      desc:'Slim-fit blazer in classic navy. Italian wool blend for a sophisticated look. Perfect for formal and business occasions.'},

  {id:3,  gender:'men', name:'Black Skinny Jeans',             brand:'DenimCo',   cat:'pants',   price:4100, old:5500,  img:'https://images.unsplash.com/photo-1542272604-787c3835535d?w=600&q=80', rating:4.6, rev:156, badge:null,   sizes:['28','30','32','34','36','38'], desc:'Stretch denim skinny jeans with flattering fit. Premium denim blend for all-day comfort.'},

  {id:4,  gender:'men', name:'Sky Blue Linen Shirt',           brand:'Breezy',    cat:'shirts',  price:2200, old:3000,  img:'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=600&q=80', rating:4.6, rev:112, badge:null,   sizes:['S','M','L','XL','XXL'],       desc:'Lightweight linen shirt perfect for summer. Natural breathable fabric keeps you cool all day.'},

  {id:5,  gender:'men', name:'Charcoal Slim Fit Suit',         brand:'Elegance',  cat:'suits',   price:24000,old:35000, img:'https://images.unsplash.com/photo-1594938298603-c8148c4b4a8c?w=600&q=80', rating:5.0, rev:32,  badge:'sale', sizes:['S','M','L','XL'],             desc:'Two-piece slim fit suit in charcoal grey. Perfect for formal events and weddings.'},

  {id:6,  gender:'men', name:'Leather Biker Jacket',           brand:'Luxe',      cat:'jackets', price:18000,old:26000, img:'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=600&q=80', rating:4.9, rev:45,  badge:'sale', sizes:['S','M','L','XL'],             desc:'Premium genuine leather biker jacket. Timeless style with YKK zippers and quilted lining.'},

  {id:7,  gender:'men', name:'Beige Chino Trousers',           brand:'FormFit',   cat:'pants',   price:3800, old:5000,  img:'https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=600&q=80', rating:4.7, rev:67,  badge:'new',  sizes:['28','30','32','34','36'],      desc:'Versatile chino in warm beige. Smart-casual style with comfortable stretch fabric.'},

  {id:8,  gender:'men', name:'Grey Crew Neck Sweatshirt',      brand:'CozyWear',  cat:'tops',    price:2600, old:3400,  img:'https://images.unsplash.com/photo-1556821840-3a63f15732ce?w=600&q=80', rating:4.7, rev:203, badge:null,   sizes:['S','M','L','XL','XXL'],       desc:'Super soft fleece sweatshirt in classic grey. Perfect for casual days and outdoor activities.'},

  {id:9,  gender:'men', name:'Burgundy Formal Shirt',          brand:'Elegance',  cat:'shirts',  price:3200, old:4200,  img:'https://images.unsplash.com/photo-1603252109303-2751441dd157?w=600&q=80', rating:4.8, rev:89,  badge:null,   sizes:['S','M','L','XL','XXL'],       desc:'Rich burgundy formal shirt with slim fit. Perfect for evening events and formal occasions.'},

  {id:10, gender:'men', name:'Black Zip-Up Hoodie',            brand:'SportLine', cat:'tops',    price:3200, old:4200,  img:'https://images.unsplash.com/photo-1509942774463-acf339cf87d5?w=600&q=80', rating:4.7, rev:267, badge:'sale', sizes:['S','M','L','XL','XXL'],       desc:'Classic zip-up hoodie in jet black. Warm fleece lining with kangaroo pocket. Gym or casual.'},

  {id:11, gender:'men', name:'White Formal Suit',              brand:'Luxe',      cat:'suits',   price:32000,old:45000, img:'https://images.unsplash.com/photo-1621072156002-e2fccdc0b176?w=600&q=80', rating:4.9, rev:28,  badge:'new',  sizes:['S','M','L','XL'],             desc:'Stunning white three-piece suit. Premium fabric with expert tailoring. Perfect for weddings.'},

  {id:12, gender:'men', name:'Graphic Print T-Shirt',          brand:'UrbanWear', cat:'tops',    price:1400, old:1900,  img:'https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=600&q=80', rating:4.4, rev:312, badge:null,   sizes:['XS','S','M','L','XL','XXL'],  desc:'Cool graphic print tee in 100% organic cotton. Relaxed fit for everyday casual wear.'},

  // ═══════════════════════════════════════════
  //  WOMEN — 12 Products (Age 18-35)
  // ═══════════════════════════════════════════

  {id:13, gender:'women', name:'Floral Wrap Summer Dress',     brand:'Blossom',   cat:'dresses', price:3200, old:4200,  img:'https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=600&q=80', rating:4.7, rev:203, badge:'new',  sizes:['XS','S','M','L'],             desc:'Light airy floral wrap dress for warm weather. Sustainable fabric. Flattering for all body types.'},

  {id:14, gender:'women', name:'Power Blazer Dress',           brand:'Luxe',      cat:'dresses', price:6500, old:9000,  img:'https://images.unsplash.com/photo-1552664730-d307ca884978?w=600&q=80', rating:4.8, rev:78,  badge:'new',  sizes:['XS','S','M','L'],             desc:'Sophisticated blazer dress for modern women. Day to night versatility with structured shoulders.'},

  {id:15, gender:'women', name:'Black High-Waist Leggings',    brand:'FitFlex',   cat:'pants',   price:2100, old:2800,  img:'https://images.unsplash.com/photo-1506629082955-511b1aa562c8?w=600&q=80', rating:4.7, rev:189, badge:'sale', sizes:['XS','S','M','L','XL'],        desc:'Sculpting high-waist leggings in 4-way stretch fabric. Perfect for yoga, gym, or daily wear.'},

  {id:16, gender:'women', name:'Satin Slip Dress — Nude',      brand:'Luxe',      cat:'dresses', price:5500, old:7800,  img:'https://images.unsplash.com/photo-1614252235316-8c857d38b5f4?w=600&q=80', rating:4.8, rev:134, badge:'sale', sizes:['XS','S','M','L'],             desc:'Luxurious satin slip dress in nude. Minimalist design with adjustable straps for evening events.'},

  {id:17, gender:'women', name:'Classic Black Blazer',         brand:'FormFit',   cat:'jackets', price:7200, old:9500,  img:'https://images.unsplash.com/photo-1548454782-15b189d129ab?w=600&q=80', rating:4.9, rev:201, badge:'new',  sizes:['XS','S','M','L'],             desc:'Classic black blazer with structured shoulders. Single button closure with slim lapels.'},

  {id:18, gender:'women', name:'High-Waist Mom Jeans',         brand:'DenimCo',   cat:'pants',   price:4200, old:5600,  img:'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=600&q=80', rating:4.7, rev:223, badge:'sale', sizes:['24','26','28','30','32'],      desc:'Trendy high-waist mom jeans in classic blue. Relaxed fit through the hip and thigh.'},

  {id:19, gender:'women', name:'Emerald Green Evening Gown',   brand:'Luxe',      cat:'dresses', price:12000,old:18000, img:'https://images.unsplash.com/photo-1566174053879-31528523f8ae?w=600&q=80', rating:5.0, rev:34,  badge:'new',  sizes:['XS','S','M','L'],             desc:'Stunning emerald green floor-length gown. Perfect for galas, weddings, and formal events.'},

  {id:20, gender:'women', name:'Camel Trench Coat',            brand:'FormFit',   cat:'jackets', price:14500,old:20000, img:'https://images.unsplash.com/photo-1539533018447-63fcce2678e3?w=600&q=80', rating:4.9, rev:78,  badge:'sale', sizes:['XS','S','M','L'],             desc:'Iconic camel trench coat with belt detail. Timeless design in water-resistant fabric.'},

  {id:21, gender:'women', name:'Cream Oversized Knit Sweater', brand:'CozyWear',  cat:'tops',    price:3100, old:4200,  img:'https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=600&q=80', rating:4.7, rev:167, badge:null,   sizes:['XS','S','M','L','XL'],        desc:'Ultra-soft oversized knit sweater. Chunky ribbed knit with drop shoulder design.'},

  {id:22, gender:'women', name:'Floral Midi Skirt',            brand:'Blossom',   cat:'skirts',  price:2900, old:3800,  img:'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=600&q=80', rating:4.6, rev:178, badge:null,   sizes:['XS','S','M','L','XL'],        desc:'Beautiful floral print midi skirt with flowing silhouette. Elastic waist for all-day comfort.'},

  {id:23, gender:'women', name:'White Linen Co-ord Set',       brand:'Breezy',    cat:'suits',   price:5800, old:7500,  img:'https://images.unsplash.com/photo-1618932260643-eee4a2f652a6?w=600&q=80', rating:4.8, rev:89,  badge:'new',  sizes:['XS','S','M','L'],             desc:'Elegant white linen co-ord blazer and wide-leg trousers. Perfect for summer events.'},

  {id:24, gender:'women', name:'Yoga Sports Set',              brand:'FitFlex',   cat:'suits',   price:4200, old:5800,  img:'https://images.unsplash.com/photo-1518611012118-696072aa579a?w=600&q=80', rating:4.8, rev:312, badge:'new',  sizes:['XS','S','M','L','XL'],        desc:'High-performance yoga set. 4-way stretch moisture-wicking fabric. Perfect for gym and active lifestyle.'},

  // ═══════════════════════════════════════════
  //  BOYS — 8 Products (Age 8-16, Teen/Young)
  // ═══════════════════════════════════════════

  {id:25, gender:'boys', name:'Boys Slim Fit Shirt — White',   brand:'KidStyle',  cat:'shirts',  price:1200, old:1600,  img:'https://images.unsplash.com/photo-1503944583220-79d8926ad5e2?w=600&q=80', rating:4.7, rev:134, badge:'new',  sizes:['8Y','10Y','12Y','14Y','16Y'], desc:'Smart slim fit white shirt for boys. Soft cotton blend, easy iron. Perfect for school and events.'},

  {id:26, gender:'boys', name:'Boys Casual Denim Jeans',       brand:'DenimCo',   cat:'pants',   price:1800, old:2400,  img:'https://images.unsplash.com/photo-1542272604-787c3835535d?w=600&q=80', rating:4.6, rev:98,  badge:null,   sizes:['8Y','10Y','12Y','14Y','16Y'], desc:'Classic slim-fit jeans for boys. Durable stretch denim with adjustable waistband.'},

  {id:27, gender:'boys', name:'Boys Sports Tracksuit',         brand:'SportLine', cat:'sets',    price:2800, old:3800,  img:'https://images.unsplash.com/photo-1503944583220-79d8926ad5e2?w=600&q=80', rating:4.7, rev:89,  badge:'sale', sizes:['8Y','10Y','12Y','14Y','16Y'], desc:'Comfortable sports tracksuit in moisture-wicking fabric. Great for school sports and outdoor activities.'},

  {id:28, gender:'boys', name:'Boys Graphic Tee — Cool',       brand:'UrbanWear', cat:'tops',    price:890,  old:1200,  img:'https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=600&q=80', rating:4.5, rev:187, badge:null,   sizes:['8Y','10Y','12Y','14Y','16Y'], desc:'Cool graphic print tee in soft cotton. Fun designs for everyday casual wear.'},

  {id:29, gender:'boys', name:'Boys Navy Blue Blazer',         brand:'FormFit',   cat:'jackets', price:4500, old:6000,  img:'https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=600&q=80', rating:4.8, rev:56,  badge:'new',  sizes:['8Y','10Y','12Y','14Y','16Y'], desc:'Smart navy blazer for special occasions. Tailored fit for a polished look at events and school.'},

  {id:30, gender:'boys', name:'Boys Chino Pants — Beige',      brand:'FormFit',   cat:'pants',   price:1600, old:2200,  img:'https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=600&q=80', rating:4.6, rev:112, badge:null,   sizes:['8Y','10Y','12Y','14Y','16Y'], desc:'Smart casual chino pants for boys. Comfortable stretch fabric with modern slim fit.'},

  {id:31, gender:'boys', name:'Boys Zip Hoodie — Black',       brand:'CozyWear',  cat:'tops',    price:1800, old:2400,  img:'https://images.unsplash.com/photo-1509942774463-acf339cf87d5?w=600&q=80', rating:4.6, rev:143, badge:null,   sizes:['8Y','10Y','12Y','14Y','16Y'], desc:'Cool zip-up hoodie for boys. Warm fleece lining. Perfect for casual outings and school.'},

  {id:32, gender:'boys', name:'Boys Formal Suit Set',          brand:'Elegance',  cat:'suits',   price:5500, old:7500,  img:'https://images.unsplash.com/photo-1594938298603-c8148c4b4a8c?w=600&q=80', rating:4.9, rev:45,  badge:'sale', sizes:['8Y','10Y','12Y','14Y','16Y'], desc:'Complete formal suit set for boys. Smart jacket and trousers. Perfect for weddings and events.'},

  // ═══════════════════════════════════════════
  //  GIRLS — 8 Products (Age 8-16, Teen/Young)
  // ═══════════════════════════════════════════

  {id:33, gender:'girls', name:'Girls Floral Dress — Pink',    brand:'Blossom',   cat:'dresses', price:1900, old:2600,  img:'https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=600&q=80', rating:4.8, rev:198, badge:'new',  sizes:['8Y','10Y','12Y','14Y','16Y'], desc:'Sweet floral dress with smocked bodice. 100% cotton for maximum comfort. Perfect for parties.'},

  {id:34, gender:'girls', name:'Girls Denim Jacket',           brand:'DenimCo',   cat:'jackets', price:2800, old:3800,  img:'https://images.unsplash.com/photo-1601333144130-8cbb312386b6?w=600&q=80', rating:4.7, rev:134, badge:null,   sizes:['8Y','10Y','12Y','14Y','16Y'], desc:'Trendy cropped denim jacket for girls. Light blue wash with distressed details. Pairs with everything.'},

  {id:35, gender:'girls', name:'Girls School Uniform Set',     brand:'TinyTots',  cat:'sets',    price:2200, old:3000,  img:'https://images.unsplash.com/photo-1503944583220-79d8926ad5e2?w=600&q=80', rating:4.9, rev:212, badge:null,   sizes:['8Y','10Y','12Y','14Y','16Y'], desc:'Complete school uniform set with shirt and skirt. Durable easy-care fabric. Smart look all day.'},

  {id:36, gender:'girls', name:'Girls Casual T-Shirt — White', brand:'Breezy',    cat:'tops',    price:890,  old:1200,  img:'https://images.unsplash.com/photo-1485462537746-965f33f7f6a7?w=600&q=80', rating:4.5, rev:167, badge:null,   sizes:['8Y','10Y','12Y','14Y','16Y'], desc:'Simple soft white tee for girls. 100% breathable cotton. Pairs with jeans, skirts and everything.'},

  {id:37, gender:'girls', name:'Girls Midi Skirt — Floral',    brand:'Blossom',   cat:'skirts',  price:1600, old:2200,  img:'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=600&q=80', rating:4.7, rev:145, badge:'new',  sizes:['8Y','10Y','12Y','14Y','16Y'], desc:'Lovely floral midi skirt for girls. Soft flowing fabric with elastic waist. Great for school and outings.'},

  {id:38, gender:'girls', name:'Girls Party Dress — Purple',   brand:'LittleLuxe',cat:'dresses', price:3200, old:4500,  img:'https://images.unsplash.com/photo-1566174053879-31528523f8ae?w=600&q=80', rating:4.9, rev:89,  badge:'sale', sizes:['8Y','10Y','12Y','14Y','16Y'], desc:'Stunning purple party dress with tulle skirt. Perfect for birthdays, events and celebrations.'},

  {id:39, gender:'girls', name:'Girls Knit Cardigan — Pink',   brand:'CozyWear',  cat:'tops',    price:1500, old:2000,  img:'https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=600&q=80', rating:4.6, rev:89,  badge:null,   sizes:['8Y','10Y','12Y','14Y','16Y'], desc:'Soft pink knit cardigan for girls. Button front with cozy ribbed knit. Perfect layering piece.'},

  {id:40, gender:'girls', name:'Girls Leggings + Top Set',     brand:'FitFlex',   cat:'sets',    price:1800, old:2500,  img:'https://images.unsplash.com/photo-1518611012118-696072aa579a?w=600&q=80', rating:4.7, rev:156, badge:'new',  sizes:['8Y','10Y','12Y','14Y','16Y'], desc:'Comfortable leggings and matching top set. Stretch fabric for active girls. Great for school and play.'},

  // ═══════════════════════════════════════════
  //  MID-AGE — 10 Products (Age 35-55)
  // ═══════════════════════════════════════════

  {id:41, gender:'mid-age', name:'Classic Formal Blazer — Grey',  brand:'Elegance',  cat:'jackets', price:9500, old:13000, img:'https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=600&q=80', rating:4.9, rev:78,  badge:'new',  sizes:['S','M','L','XL','XXL'],      desc:'Sophisticated grey formal blazer. Timeless cut for the modern professional. Office to dinner ready.'},

  {id:42, gender:'mid-age', name:'Premium Polo Shirt — Navy',     brand:'FormFit',   cat:'shirts',  price:2800, old:3800,  img:'https://images.unsplash.com/photo-1571945153237-4929e783af4a?w=600&q=80', rating:4.8, rev:134, badge:null,   sizes:['S','M','L','XL','XXL'],      desc:'Premium pique cotton polo in classic navy. Elegant and comfortable for daily wear.'},

  {id:43, gender:'mid-age', name:'Comfortable Stretch Trousers',  brand:'FormFit',   cat:'pants',   price:4200, old:5800,  img:'https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=600&q=80', rating:4.7, rev:167, badge:null,   sizes:['28','30','32','34','36','38'], desc:'Smart stretch trousers with comfortable waistband. Professional look with all-day comfort.'},

  {id:44, gender:'mid-age', name:'Classic Kurta — White',         brand:'Heritage',  cat:'shirts',  price:3200, old:4500,  img:'https://images.unsplash.com/photo-1602810316693-3667c854239a?w=600&q=80', rating:4.8, rev:189, badge:'new',  sizes:['S','M','L','XL','XXL'],      desc:'Elegant white cotton kurta. Classic design with modern comfort. Perfect for casual and formal occasions.'},

  {id:45, gender:'mid-age', name:'Formal Dark Suit',              brand:'Elegance',  cat:'suits',   price:28000,old:40000, img:'https://images.unsplash.com/photo-1594938298603-c8148c4b4a8c?w=600&q=80', rating:5.0, rev:45,  badge:'sale', sizes:['S','M','L','XL','XXL'],      desc:'Classic dark navy suit. Expert tailoring for the distinguished professional. Timeless and elegant.'},

  {id:46, gender:'mid-age', name:'Elegant Saree Blouse Set',      brand:'Heritage',  cat:'suits',   price:8500, old:12000, img:'https://images.unsplash.com/photo-1618932260643-eee4a2f652a6?w=600&q=80', rating:4.9, rev:56,  badge:'new',  sizes:['XS','S','M','L','XL'],       desc:'Beautiful saree blouse set in premium silk blend. Elegant embroidery detail. Perfect for celebrations.'},

  {id:47, gender:'mid-age', name:'Comfort Linen Shirt — Blue',    brand:'Breezy',    cat:'shirts',  price:2600, old:3500,  img:'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=600&q=80', rating:4.7, rev:112, badge:null,   sizes:['S','M','L','XL','XXL'],      desc:'Relaxed linen shirt in calming blue. Breathable fabric for warm weather. Casual yet polished.'},

  {id:48, gender:'mid-age', name:'Elegant Midi Dress — Maroon',   brand:'Luxe',      cat:'dresses', price:5500, old:7500,  img:'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=600&q=80', rating:4.8, rev:89,  badge:'sale', sizes:['XS','S','M','L','XL'],       desc:'Sophisticated maroon midi dress. A-line silhouette flatters all body types. Perfect for family events.'},

  {id:49, gender:'mid-age', name:'Classic Wrap Dress — Floral',   brand:'Blossom',   cat:'dresses', price:4200, old:5800,  img:'https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=600&q=80', rating:4.7, rev:134, badge:null,   sizes:['XS','S','M','L','XL'],       desc:'Beautiful floral wrap dress. Flattering wrap silhouette with adjustable tie. Day or evening ready.'},

  {id:50, gender:'mid-age', name:'Premium Wool Overcoat',         brand:'FormFit',   cat:'jackets', price:18000,old:26000, img:'https://images.unsplash.com/photo-1544022613-e87ca75a784a?w=600&q=80', rating:4.9, rev:67,  badge:'sale', sizes:['S','M','L','XL','XXL'],      desc:'Premium wool-blend overcoat in charcoal. Timeless design for the distinguished wardrobe.'},

];

/* ════════════════════════════════════════════
   CART FUNCTIONS
════════════════════════════════════════════ */
function getCart()   { return JSON.parse(localStorage.getItem('vf_cart') || '[]'); }
function saveCart(c) { localStorage.setItem('vf_cart', JSON.stringify(c)); updateBadge(); }
function getUser() {
  const u = JSON.parse(localStorage.getItem('vf_user') || 'null');
  if(!u) return null;
  // Clear stale data if token is missing
  const tok = localStorage.getItem('vf_token');
  if(!tok) { 
    localStorage.removeItem('vf_user');
    return null;
  }
  return u;
}

function isTokenExpired() {
  const tok = getToken();
  if(!tok) return true;
  try {
    // JWT is base64 encoded: header.payload.signature
    const parts = tok.split('.');
    if(parts.length !== 3) return true;
    const payload = JSON.parse(atob(parts[1]));
    // Check exp claim (seconds since epoch)
    if(payload.exp && Date.now() / 1000 > payload.exp) {
      // Token expired - clear storage
      localStorage.removeItem('vf_user');
      localStorage.removeItem('vf_token');
      return true;
    }
    return false;
  } catch(e) {
    return true;
  }
}
function getToken()  { return localStorage.getItem('vf_token') || ''; }

// Auth-aware fetch helper - automatically adds JWT token
async function authFetch(url, options = {}) {
  const token = getToken();
  // Backend validates token - no client redirect needed
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };
  if(token) headers['Authorization'] = 'Bearer ' + token;
  return fetch(url, { ...options, headers });
}

// Check if user is logged in
function isLoggedIn() {
  const u = getUser();
  const t = getToken();
  return !!(u && t && u.id);
}

// Logout helper
function doLogout() {
  localStorage.removeItem('vf_user');
  localStorage.removeItem('vf_token');
  location.href = 'login.html';
}

function addToCart(product) {
  const cart = getCart();
  const ex = cart.find(i => i.id === product.id && i.size === product.size);
  if (ex) ex.qty++;
  else cart.push({ ...product, qty: 1 });
  saveCart(cart);
  toast(product.name + ' added to cart! 🛍️');
}

function updateBadge() {
  const n = getCart().reduce((s, i) => s + i.qty, 0);
  document.querySelectorAll('#cartBadge').forEach(b => b.textContent = n);
}

/* ════════════════════════════════════════════
   TOAST
════════════════════════════════════════════ */
function toast(msg, type = 'ok') {
  const icons = { ok:'check-circle', err:'exclamation-circle', info:'info-circle' };
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.innerHTML = `<i class="fas fa-${icons[type]||'info-circle'}"></i>${msg}`;
  document.body.appendChild(t);
  requestAnimationFrame(() => requestAnimationFrame(() => t.classList.add('show')));
  setTimeout(() => { t.classList.remove('show'); setTimeout(() => t.remove(), 350); }, 3500);
}

/* ════════════════════════════════════════════
   PRODUCT CARD — Real Images
════════════════════════════════════════════ */
function productCard(p) {
  const pct = p.old ? Math.round((1 - p.price / p.old) * 100) : 0;
  const genderLabel = {men:'Men', women:'Women', boys:'Boys', girls:'Girls', 'mid-age':'Mid-Age'}[p.gender] || p.gender;
  return `
<div class="product-card" onclick="location='product.html?id=${p.id}'">
  <div class="pcard-img">
    <img src="${p.img}" alt="${p.name}" style="width:100%;height:100%;object-fit:cover" loading="lazy"
         onerror="this.style.display='none'">
    ${p.badge ? `<span class="pcard-badge ${p.badge}">${p.badge}</span>` : ''}
    <span class="pcard-gender">${genderLabel}</span>
    <div class="pcard-overlay">
      <button class="btn btn-gold btn-sm btn-full" onclick="event.stopPropagation();quickAdd(${p.id})">
        <i class="fas fa-shopping-bag"></i> Add to Cart
      </button>
      <button class="btn btn-outline btn-sm btn-full" onclick="event.stopPropagation();location='tryon.html?id=${p.id}'">
        <i class="fas fa-camera"></i> Try On ✨
      </button>
    </div>
  </div>
  <div class="pcard-info">
    <div class="pcard-brand">${p.brand}</div>
    <div class="pcard-name">${p.name}</div>
    <div class="pcard-price">
      Rs. ${p.price.toLocaleString()}
      ${p.old ? `<span class="old">Rs. ${p.old.toLocaleString()}</span>` : ''}
      ${pct > 0 ? `<span style="font-size:11px;color:var(--red);margin-left:6px;font-weight:700">${pct}% off</span>` : ''}
    </div>
    <div class="pcard-rating">
      <span class="stars">${'★'.repeat(Math.round(p.rating))}${'☆'.repeat(5-Math.round(p.rating))}</span>
      <span style="font-size:11px;color:var(--muted);margin-left:4px">(${p.rev})</span>
    </div>
  </div>
</div>`;
}

// ── LOAD ADMIN CUSTOM PRODUCTS ───────────────────────────
(function() {
  try {
    const custom = JSON.parse(localStorage.getItem('vf_custom_products') || '[]');
    custom.forEach(p => {
      const idx = PRODUCTS.findIndex(x => x.id === p.id);
      if(idx >= 0) PRODUCTS[idx] = p; // update existing
      else PRODUCTS.push(p);          // add new
    });
  } catch(e) {}
})();

function quickAdd(id) {
  const p = PRODUCTS.find(x => x.id === id);
  if (!p) return;
  const size = p.sizes[Math.floor(p.sizes.length / 2)];
  addToCart({ id:p.id, name:p.name, price:p.price, img:p.img, size, gender:p.gender });
}
