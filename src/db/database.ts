import { Sequelize } from 'sequelize';

const sequelize = new Sequelize(process.env.POSTGRES_DATABASE as string, process.env.POSTGRES_USER as string, process.env.POSTGRES_PASSWORD as string, {
    host:  process.env.POSTGRES_HOST as string,
    dialect: 'mariadb',
    define: {
        freezeTableName: true,
    }
});

export default sequelize;
