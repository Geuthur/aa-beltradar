function BaseSectionHeader({ name }: { name: string }) {
    return (
        <>
            <section className="card" aria-labelledby="session-heading">
                <div className="card-header bg-primary rounded">
                    <h3 id="session-heading">{name}</h3>
                </div>
            </section>
        </>
    );
};

export default BaseSectionHeader;
