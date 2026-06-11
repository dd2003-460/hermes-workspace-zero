#!/usr/bin/env python3
"""
S17-1 实证验证 v2: 语义空间信息几何
=====================================

核心改变: 不用cosine distance（TF-IDF归一化后全为1.0），
改用 **Jensen-Shannon散度** 和 **词汇重叠率** 作为语义距离度量。

JSD(p||q) = KL(p||M) + KL(q||M), M=(p+q)/2
- 对于分布，JSD ∈ [0, 1]
- 语义相似的概念分布更重叠，JSD更小
"""

import numpy as np
from scipy.spatial.distance import jensenshannon
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import json, os, time

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "researches")


def build_concept_corpus():
    """扩展概念集合，每个概念用10个句子描述（增加词汇重叠）"""
    concepts = {
        # 动物（共享"动物"相关词汇）
        "animal": [
            "An animal is a living organism that moves and eats.",
            "Animals have senses and can feel pain and pleasure.",
            "Most animals need food water and shelter to survive.",
            "Cats and dogs are common pets kept in homes.",
            "Birds fly in the sky while fish swim in the water.",
            "Animals give birth to young ones that grow up.",
            "Wild animals live in forests deserts and mountains.",
            "Pets like cats and dogs love their owners.",
            "Animals communicate through sounds body language and scents.",
            "The animal kingdom has millions of known species.",
        ],
        "mammal": [
            "Mammals are warm blooded animals that nurse their young.",
            "Dogs and cats are mammals with fur on their bodies.",
            "Humans are mammals just like whales and elephants.",
            "Mammals have hair or fur and produce milk for their babies.",
            "Most mammals give birth to live young instead of laying eggs.",
            "Elephants are the largest land mammals on Earth.",
            "Dogs are loyal mammals trained as companions and workers.",
            "Cats are independent mammals that hunt small prey.",
            "Mammals have four legs and a tail.",
            "The whale is the largest mammal that ever lived.",
        ],
        "dog": [
            "A dog is a domesticated animal that barks and wags its tail.",
            "Dogs are loyal pets known as man's best friend.",
            "Labrador retrievers are a friendly and energetic breed of dog.",
            "Dogs can be trained to perform many tasks and tricks.",
            "Golden retrievers are gentle dogs loved by families.",
            "Dogs need exercise walks and playtime every day.",
            "German shepherds are intelligent working dogs.",
            "Dogs understand human emotions and respond to moods.",
            "A dog owner takes their dog to the park daily.",
            "Labrador dogs are the most popular pet breed.",
        ],
        "labrador": [
            "Labrador retrievers are large friendly dogs with short coats.",
            "Labradors are energetic dogs bred for hunting and retrieving.",
            "Labrador dogs are excellent family pets and service animals.",
            "Labradors come in black chocolate and yellow colors.",
            "A Labrador puppy needs lots of exercise and training.",
            "Labrador retrievers have webbed paws for swimming.",
            "Labradors are among the smartest dog breeds in the world.",
            "The Labrador is the most registered dog breed worldwide.",
            "Labrador dogs are hypoallergenic due to their short fur.",
            "Labradors are great with children and other pets.",
        ],
        "cat": [
            "A cat is a small domesticated feline that purrs and hunts mice.",
            "Cats are independent pets that groom themselves.",
            "Persian cats are fluffy long haired domestic cats.",
            "Cats sleep 12 to 16 hours a day.",
            "A cat owner fills their cat bowl with food daily.",
            "Cats have excellent night vision and hearing.",
            "Cats play with toys like yarn balls and feather wands.",
            "Cats can jump up to six times their body height.",
            "The cat is one of the most popular pets in the world.",
            "Cats communicate through meowing hissing and body language.",
        ],
        "bird": [
            "A bird is a feathered animal that flies in the sky.",
            "Birds lay eggs and build nests in trees.",
            "Sparrows are small brown birds found everywhere.",
            "Eagles are large birds of prey that hunt rabbits.",
            "Birds have hollow bones to help them fly.",
            "Canaries are colorful birds that sing beautiful melodies.",
            "Birds migrate south for the winter to find food.",
            "Penguins are flightless birds that live in Antarctica.",
            "Parrots are intelligent birds that can mimic human speech.",
            "Birdwatching is a popular hobby around the world.",
        ],
        # 交通工具（共享"交通工具"相关词汇）
        "vehicle": [
            "A vehicle is a machine used for transportation of people and goods.",
            "Vehicles move on roads rails or through the air and water.",
            "Cars and trucks are land vehicles that use engines.",
            "Airplanes are flying vehicles that carry passengers across continents.",
            "Bicycles are simple human powered vehicles with two wheels.",
            "Vehicles require fuel electricity or animal power to operate.",
            "Traffic laws regulate how vehicles move on public roads.",
            "Vehicle maintenance includes oil changes tire rotation and brake checks.",
            "Public vehicles like buses and trains carry many passengers.",
            "The vehicle industry produces millions of machines each year.",
        ],
        "land_vehicle": [
            "Land vehicles move on roads rails and tracks on the ground.",
            "Cars trucks and bicycles are common land vehicles in cities.",
            "Land vehicles use wheels tracks or skis for movement.",
            "Cars are the most popular land vehicles for personal transport.",
            "Trains are large land vehicles that run on steel rails.",
            "Land vehicles emit pollution from burning fossil fuels.",
            "Electric land vehicles like Tesla cars produce zero emissions.",
            "Trucks are heavy land vehicles used for cargo transport.",
            "Motorcycles are fast two wheeled land vehicles.",
            "Land vehicles need regular maintenance and fuel or electricity.",
        ],
        "car": [
            "A car is a four wheeled motorized vehicle for personal transport.",
            "Cars have engines seats steering wheels and brakes.",
            "Sedans and SUVs are common types of cars on the road.",
            "Tesla makes electric cars that run on battery power.",
            "Cars need regular maintenance oil changes and tire rotations.",
            "A car owner pays for gas insurance and parking.",
            "Red cars and blue cars are the most common colors.",
            "Cars can accelerate brake turn and reverse.",
            "The car industry employs millions of workers worldwide.",
            "Luxury cars like Mercedes and BMW are expensive vehicles.",
        ],
        "train": [
            "A train is a large land vehicle that runs on steel rails.",
            "Trains pull many carriages full of passengers and cargo.",
            "High speed trains like the Shinkansen travel over 200 mph.",
            "Trains run on fixed tracks and schedules.",
            "Cargo trains carry containers and raw materials across countries.",
            "A train conductor checks tickets and operates the engine.",
            "Steam trains use coal or wood to power the engine.",
            "Subway trains run underground in big cities.",
            "Trains are one of the most energy efficient land vehicles.",
            "Railway stations serve thousands of train passengers daily.",
        ],
        "aircraft": [
            "An aircraft is a vehicle that flies in the sky using wings.",
            "Airplanes are large aircraft that carry hundreds of passengers.",
            "Helicopters are rotating wing aircraft that can hover.",
            "Aircraft need long runways to take off and land.",
            "Pilots fly aircraft through clouds and storms.",
            "Fighter jets are fast military aircraft.",
            "Aircraft use jet engines or propellers for thrust.",
            "Air traffic controllers guide aircraft in the sky.",
            "The Wright brothers built the first successful aircraft in 1903.",
            "Cargo aircraft transport goods between countries.",
        ],
        # 食物
        "food": [
            "Food is any substance eaten to provide nutrition and energy.",
            "Humans eat food three times a day for meals.",
            "Food can be cooked raw fermented or dried for preservation.",
            "Food quality depends on freshness and preparation methods.",
            "Restaurants serve food to customers from many cuisines.",
            "Food safety requires proper storage and temperature control.",
            "Food contains carbohydrates proteins fats vitamins and minerals.",
            "Hunger is the body's signal that it needs food.",
            "Food waste is a major environmental concern worldwide.",
            "A balanced food diet includes fruits vegetables and grains.",
        ],
        "fruit": [
            "Fruits are sweet plant foods that contain seeds.",
            "Apples bananas and oranges are the most popular fruits.",
            "Fruits are rich in vitamins fiber and natural sugars.",
            "Fresh fruits are grown in orchards and farms.",
            "Dried fruits like raisins and dates are healthy snacks.",
            "Fruits can be eaten raw juiced or baked into desserts.",
            "Tropical fruits like mangoes grow in hot climates.",
            "Berries are small sweet fruits grown in gardens.",
            "Fruits provide natural energy antioxidants and nutrients.",
            "Seasonal fruits taste fresher and sweeter.",
        ],
        "apple": [
            "An apple is a round crisp fruit that grows on apple trees.",
            "Red apples and green apples are the most common varieties.",
            "Apple pie is a classic dessert made from baked apples.",
            "Apples are sweet crunchy fruits packed with fiber.",
            "Apple trees bloom in spring and bear fruit in autumn.",
            "Apples grow in orchards in temperate climates.",
            "Apple juice and cider are made from pressed apples.",
            "The apple is one of the most consumed fruits worldwide.",
            "Granny Smith apples are tart and green in color.",
            "Apples are low in calories and great for snacks.",
        ],
        "banana": [
            "A banana is a long yellow tropical fruit with soft sweet flesh.",
            "Bananas grow in bunches on large herbaceous plants.",
            "Bananas are rich in potassium vitamin B6 and fiber.",
            "Banana smoothies and banana bread are popular recipes.",
            "Bananas are one of the most exported fruits globally.",
            "Green bananas turn yellow as they ripen naturally.",
            "Banana trees are not true trees but giant herbs.",
            "Bananas provide quick energy and are easy to digest.",
            "The Cavendish is the most common banana variety sold in stores.",
            "Banana leaves are used as natural food wraps.",
        ],
        "vegetable": [
            "Vegetables are plant foods that are savory rather than sweet.",
            "Leafy vegetables like spinach and lettuce are very healthy.",
            "Root vegetables like carrots and potatoes grow underground.",
            "Vegetables contain fiber vitamins and minerals essential for health.",
            "Fresh vegetables should be eaten daily for a balanced diet.",
            "Garden vegetables include tomatoes peppers cucumbers and beans.",
            "Cooked vegetables are softer and easier to digest.",
            "Organic vegetables are grown without pesticides or fertilizers.",
            "Vegetables are the base of soups salads and stir fries.",
            "Vegetable gardens provide fresh produce for home cooks.",
        ],
        # 颜色
        "color": [
            "A color is a visual property of objects perceived by the eye.",
            "Colors are produced by different wavelengths of light.",
            "Red blue and yellow are the primary colors in art.",
            "Colors can evoke emotions warm colors feel energetic.",
            "The color wheel arranges all colors in a circle.",
            "Color theory helps artists and designers choose harmonious palettes.",
            "Colors appear different under natural and artificial light.",
            "Color blindness affects the ability to distinguish some colors.",
            "Digital screens create colors using red green and blue pixels.",
            "Color psychology studies how colors influence human behavior.",
        ],
        "red": [
            "Red is a warm primary color associated with passion and danger.",
            "Red lights signal stop and red flags warn of danger.",
            "Red flowers like roses symbolize love and romance.",
            "Red is the first color of the rainbow visible to humans.",
            "Red paint and red dye are widely used in art and design.",
            "Red colors include crimson burgundy scarlet and maroon.",
            "Babies can see red as their first distinguishable color.",
            "Red colors raise heart rate and create excitement.",
            "Red is a dominant color in many national flags.",
            "A red light stop sign is universal across cultures.",
        ],
        "blue": [
            "Blue is a cool primary color associated with calm and peace.",
            "Blue skies and blue oceans are the most expansive natural colors.",
            "Blue paint and blue dye are popular in design and fashion.",
            "Blue is the second color of the rainbow after red.",
            "Blue colors include navy azure cerulean and cobalt.",
            "Blue lights create a soothing and relaxing atmosphere.",
            "Blue is the most preferred color in surveys worldwide.",
            "Blue colors like sapphire and turquoise are gemstone hues.",
            "Blue is a dominant color in technology logos and branding.",
            "The color of the sky and deep water is blue.",
        ],
        # 情感
        "emotion": [
            "Emotions are complex psychological states involving feelings and thoughts.",
            "Humans experience emotions like happiness sadness and anger.",
            "Emotions influence decision making and social behavior.",
            "Facial expressions and body language communicate emotions.",
            "Emotions activate the brain's limbic system and nervous system.",
            "Positive emotions improve mental health and well being.",
            "Emotional intelligence is the ability to recognize and manage emotions.",
            "Emotions have evolutionary origins related to survival.",
            "Cultural norms shape how emotions are expressed and perceived.",
            "Emotions can be induced by music art and storytelling.",
        ],
        "happiness": [
            "Happiness is a positive emotion of joy contentment and well being.",
            "Happy people laugh smile and feel grateful for life.",
            "Happiness comes from good relationships health and purpose.",
            "The pursuit of happiness is a fundamental human drive.",
            "Happiness hormones include serotonin dopamine and oxytocin.",
            "Happy memories and happy experiences make life meaningful.",
            "Children are naturally happy and playful in their activities.",
            "Happiness is subjective and means different things to different people.",
            "Meditation and exercise are proven ways to increase happiness.",
            "A happy family environment fosters emotional development.",
        ],
        "sadness": [
            "Sadness is an emotion of sorrow grief and emotional pain.",
            "People cry when they feel deep sadness and loss.",
            "Sadness can be caused by death breakup or failure.",
            "Sad music and sad movies help people process their emotions.",
            "Prolonged sadness can lead to depression and anxiety.",
            "Sad faces show downturned mouths and tearful eyes.",
            "Sadness is a natural part of the human emotional experience.",
            "Comfort from others helps relieve sadness and pain.",
            "Seasonal sadness is common during winter months.",
            "Overcoming sadness builds emotional resilience and strength.",
        ],
        # 数学
        "mathematics": [
            "Mathematics is the science of numbers quantity structure and space.",
            "Mathematics uses logic proof and abstraction to solve problems.",
            "Mathematics is fundamental to physics chemistry and engineering.",
            "Mathematical equations describe natural laws and patterns.",
            "Mathematics includes algebra geometry analysis and statistics.",
            "Mathematicians develop theories and prove conjectures rigorously.",
            "Mathematics training develops critical thinking and problem solving.",
            "Pure mathematics explores abstract structures for their own beauty.",
            "Applied mathematics solves real world problems in science and business.",
            "The language of mathematics is universal across cultures.",
        ],
        "algebra": [
            "Algebra uses symbols and letters to represent unknown numbers.",
            "Algebraic equations like ax plus b equals zero are solved for x.",
            "Abstract algebra studies groups rings and fields.",
            "Linear algebra uses matrices and vectors for computation.",
            "Algebra is a prerequisite for calculus and higher mathematics.",
            "Algebraic manipulation allows solving complex mathematical problems.",
            "Symmetric algebra explores invariant structures under transformations.",
            "Elementary algebra teaches factoring polynomials and solving systems.",
            "Algebraic geometry connects algebra to geometric shapes.",
            "Boolean algebra is the foundation of computer science logic.",
        ],
        "geometry": [
            "Geometry studies shapes sizes positions and properties of space.",
            "Euclidean geometry is based on points lines planes and angles.",
            "Non Euclidean geometry challenges the parallel postulate.",
            "Analytic geometry uses coordinates and algebraic equations.",
            "Topology is a branch of geometry studying properties preserved under deformation.",
            "Geometric proofs use logical deduction and axioms.",
            "Geometry is essential for architecture engineering and art.",
            "Solid geometry deals with three dimensional objects like cubes and spheres.",
            "Coordinate geometry links algebra to geometric figures on graphs.",
            "Projective geometry studies properties invariant under projection.",
        ],
        "analysis": [
            "Mathematical analysis studies limits continuity derivatives and integrals.",
            "Calculus is the foundation of mathematical analysis.",
            "Real analysis rigorously defines limits and continuity.",
            "Complex analysis studies functions of complex numbers.",
            "Functional analysis extends calculus to infinite dimensional spaces.",
            "Measure theory is the rigorous foundation of integration.",
            "Differential equations are central to mathematical analysis.",
            "Analysis has applications in physics economics and engineering.",
            "Fourier analysis decomposes functions into frequency components.",
            "Number theory uses analytic methods to study prime numbers.",
        ],
    }
    return concepts


def build_tfidf_space(concepts):
    """TF-IDF空间（用句子文档集）"""
    concept_names = list(concepts.keys())
    docs = [" ".join(concepts[k]) for k in concept_names]

    vectorizer = TfidfVectorizer(max_features=500)
    tfidf_matrix = vectorizer.fit_transform(docs)

    # SVD降维
    from scipy.sparse.linalg import svds
    U, S, Vt = svds(tfidf_matrix, k=min(10, tfidf_matrix.shape[1] - 1))
    idx = np.argsort(-S)
    embeddings_low = U[:, idx] * S[idx]

    return {
        "names": concept_names,
        "embeddings_high": tfidf_matrix.toarray(),
        "embeddings_low": embeddings_low,
        "vectorizer": vectorizer,
    }


def compute_jsd_distances(data):
    """计算概念对的Jensen-Shannon散度"""
    names = data["names"]
    n = len(names)

    # TF-IDF向量归一化为概率分布
    probs = data["embeddings_high"] / (data["embeddings_high"].sum(axis=1, keepdims=True) + 1e-10)

    jsd_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            jsd = jensenshannon(probs[i], probs[j])
            jsd_matrix[i, j] = jsd
            jsd_matrix[j, i] = jsd

    return jsd_matrix, probs


def build_knn_graph_jsd(jsd_matrix, k=5):
    """用JSD距离构建k-NN图"""
    n = jsd_matrix.shape[0]
    adj = {}

    for i in range(n):
        dists = jsd_matrix[i].copy()
        dists[i] = float('inf')  # 排除自身
        nn_idx = np.argsort(dists)[:k]

        adj[i] = [(int(j), float(jsd_matrix[i, j])) for j in nn_idx]

    return adj


def dijkstra(adj, start, end, n_points):
    """Dijkstra最短路径"""
    import heapq

    n = len(adj)
    dist = [float('inf')] * n
    prev = [-1] * n
    dist[start] = 0
    pq = [(0, start)]

    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                prev[v] = u
                heapq.heappush(pq, (dist[v], v))

    if dist[end] == float('inf'):
        return [start, end], [start, end], float('inf')

    path = []
    cur = end
    while cur != -1:
        path.append(cur)
        cur = prev[cur]
    path.reverse()

    if len(path) >= n_points and n_points > 2:
        step = len(path) / max(n_points - 1, 1)
        sampled = [path[min(int(round(i * step)), len(path) - 1)] for i in range(n_points)]
    else:
        sampled = path

    return path, sampled, dist[end]


def generate_detour(adj, start, end, max_len):
    """随机游走生成绕路路径"""
    n = len(adj)
    path = [start]
    visited = {start}

    for _ in range(max_len):
        cur = path[-1]
        neighbors = [node for node, _ in adj[cur]]
        options = [j for j in neighbors if j not in visited and j != end]
        if not options:
            options = [j for j in neighbors if j != end]
        if not options:
            break
        path.append(np.random.choice(options))
        visited.add(path[-1])

    path.append(end)
    return path


def compute_path_jsd(jsd_matrix, path_indices):
    """路径上的平均JSD（路径上的语义变化）"""
    if len(path_indices) < 2:
        return 0.0

    total_jsd = sum(jsd_matrix[path_indices[i], path_indices[i+1]]
                    for i in range(len(path_indices) - 1))
    return total_jsd / (len(path_indices) - 1)


def compute_curvature(data, concept_names, k=5):
    """用TF-IDF空间局部概率分布估计曲率"""
    probs = data["embeddings_high"] / (data["embeddings_high"].sum(axis=1, keepdims=True) + 1e-10)
    n = len(concept_names)

    results = []
    for i in range(0, n, max(1, n // 15)):
        nn_idx = np.argsort(np.linalg.norm(probs - probs[i], axis=1))[1:k+1]
        local_cov = np.cov((probs[nn_idx] - probs[i]).T)
        eigvals = np.linalg.eigvalsh(local_cov)
        eigvals = eigvals[eigvals > 1e-10]
        if len(eigvals) >= 2:
            curvature = (eigvals[-1] - eigvals[0]) / (eigvals[-1] + eigvals[0] + 1e-10)
            results.append({
                "concept": concept_names[i],
                "curvature_strength": round(float(curvature), 4),
                "eigenvalues": [round(float(e), 6) for e in eigvals[:3]],
            })

    return results


def main():
    start_time = time.time()
    print("=" * 60)
    print("S17-1 实证验证 v2: 语义空间信息几何 (Jensen-Shannon)")
    print("=" * 60)

    # 1. 构建空间
    print("\n[1/5] 构建语义概念集合 + TF-IDF空间...")
    concepts = build_concept_corpus()
    data = build_tfidf_space(concepts)
    print(f"  概念数: {len(data['names'])}, TF-IDF维度: {data['embeddings_high'].shape[1]}")

    # 2. JSD距离矩阵
    print("\n[2/5] 计算Jensen-Shannon散度矩阵...")
    jsd_matrix, probs = compute_jsd_distances(data)
    name_to_idx = {n: i for i, n in enumerate(data["names"])}
    print(f"  JSD范围: [{jsd_matrix[np.triu_indices_from(jsd_matrix, k=1)].min():.4f}, "
          f"{jsd_matrix[np.triu_indices_from(jsd_matrix, k=1)].max():.4f}]")
    print(f"  JSD均值: {jsd_matrix[np.triu_indices_from(jsd_matrix, k=1)].mean():.4f}")

    # 3. 曲率
    print("\n[3/5] 估计局部曲率...")
    curvatures = compute_curvature(data, data["names"])
    if curvatures:
        strengths = [c["curvature_strength"] for c in curvatures]
        print(f"  曲率强度: {np.mean(strengths):.4f} ± {np.std(strengths):.4f}")
        print(f"  范围: [{min(strengths):.4f}, {max(strengths):.4f}]")
    else:
        strengths = []
        print("  曲率估计失败")

    # 4. 测地线 vs JSD
    print("\n[4/5] 构建k-NN图 + 测地线距离...")
    adj = build_knn_graph_jsd(jsd_matrix, k=10)
    print(f"  图节点: {len(adj)}, 每节点邻居数: 10")

    test_pairs = [
        ("dog", "labrador"), ("dog", "cat"), ("dog", "bird"),
        ("dog", "car"), ("dog", "apple"),
        ("mathematics", "geometry"), ("mathematics", "analysis"),
        ("mathematics", "happiness"),
        ("red", "blue"), ("red", "happiness"),
        ("apple", "banana"), ("apple", "vegetable"),
        ("car", "train"), ("car", "aircraft"),
    ]

    path_results = []
    for a, b in test_pairs:
        if a not in name_to_idx or b not in name_to_idx:
            continue
        ia, ib = name_to_idx[a], name_to_idx[b]
        jsd = float(jsd_matrix[ia, ib])

        path, sampled, d_geo = dijkstra(adj, ia, ib, n_points=8)
        il_short = compute_path_jsd(jsd_matrix, path)
        il_sampled = compute_path_jsd(jsd_matrix, sampled)

        path_results.append({
            "pair": [a, b],
            "jsd_direct": round(jsd, 4),
            "geodesic": round(d_geo, 4),
            "path_length": len(path),
            "path": [data["names"][p] for p in path[:10]],
            "info_loss_short": round(il_short, 4),
            "info_loss_sampled": round(il_sampled, 4),
        })

        print(f"  {a}->{b}: JSD={jsd:.4f}, geo={d_geo:.4f}, path_len={len(path)}")

    # 5. 绕路实验
    print("\n[5/5] 绕路路径信息损失实验...")
    detour_results = []
    for _ in range(50):
        ia = np.random.randint(len(data["names"]))
        ib = np.random.randint(len(data["names"]))
        if ia == ib:
            continue

        path_short, _, d_geo = dijkstra(adj, ia, ib, n_points=10)
        path_detour = generate_detour(adj, ia, ib, min(len(path_short) * 3, 30))

        il_s = compute_path_jsd(jsd_matrix, path_short)
        il_d = compute_path_jsd(jsd_matrix, path_detour)

        detour_results.append({
            "ratio": round(il_d / (abs(il_s) + 1e-10), 4),
            "path_short_len": len(path_short),
            "path_detour_len": len(path_detour),
        })

    if detour_results:
        ratios = [d["ratio"] for d in detour_results]
        print(f"  绕路/最短信息损失比: 均值={np.mean(ratios):.4f}, 中位数={np.median(ratios):.4f}")
    else:
        print("  无结果")

    elapsed = time.time() - start_time
    print(f"\n实验完成 ({elapsed:.1f}s)")

    # 保存结果
    output = {
        "summary": {
            "elapsed_seconds": elapsed,
            "n_concepts": len(data["names"]),
            "tfidf_dimension": data["embeddings_high"].shape[1],
            "jsd_stats": {
                "min": round(float(jsd_matrix[np.triu_indices_from(jsd_matrix, k=1)].min()), 4),
                "max": round(float(jsd_matrix[np.triu_indices_from(jsd_matrix, k=1)].max()), 4),
                "mean": round(float(jsd_matrix[np.triu_indices_from(jsd_matrix, k=1)].mean()), 4),
            },
            "curvature_stats": {
                "mean": round(float(np.mean(strengths)), 4) if strengths else None,
                "std": round(float(np.std(strengths)), 4) if strengths else None,
            },
            "detour_stats": {
                "mean_ratio": round(float(np.mean(ratios)), 4) if detour_results else None,
                "median_ratio": round(float(np.median(ratios)), 4) if detour_results else None,
            },
        },
        "path_results": path_results,
        "curvatures": curvatures,
        "detour_results": detour_results[:20],
    }

    out_path = os.path.join(RESULTS_DIR, "S17-1-Empirical-Results-v2.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"结果: {out_path}")
    return output


if __name__ == "__main__":
    main()
